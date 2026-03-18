import sys
import os
from datetime import datetime
from config import IMAP_HOST, IMAP_PORT, IMAP_EMAIL, IMAP_PASSWORD, WATCH_FROM_EMAILS, IMAP_LOOKBACK_DAYS
from loader import load_par_libraries
from extractor import extract_jd
from scorer import score_project
from db_logger import log_evaluation
import imaplib
import email as email_lib

def test_latest():
    print(">>> MANUAL TEST: FETCHING LATEST EMAIL...")
    
    # 1. Connect and Fetch Latest Email (Ignoring UNSEEN)
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    mail.login(IMAP_EMAIL, IMAP_PASSWORD)
    mail.select("INBOX")
    
    _, data = mail.uid("SEARCH", None, "ALL")
    uids = data[0].split()
    if not uids:
        print("  ❌ No emails found")
        return
    
    latest_uid = uids[-1]
    _, msg_data = mail.uid("FETCH", latest_uid, "(RFC822)")
    raw = msg_data[0][1]
    msg = email_lib.message_from_bytes(raw)
    
    # Decode subject
    subject = ""
    import email.header
    for part, enc in email.header.decode_header(msg.get("Subject", "")):
        if isinstance(part, bytes):
            subject += part.decode(enc or "utf-8", errors="replace")
        else:
            subject += str(part)
    
    print(f"  📩 Latest Email: {subject}")
    
    # Extract Body
    html_body = None
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html_body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                break
    elif msg.get_content_type() == "text/html":
        html_body = msg.get_payload(decode=True).decode("utf-8", errors="replace")
    
    if not html_body:
        print("  ❌ No HTML body found in latest email")
        return

    # 2. Extract JD
    title, description, platform = extract_jd(subject, html_body)
    print(f"  📝 Extracted Title: {title}")
    
    # 3. Load Libraries and Score
    par_libraries = load_par_libraries()
    evaluations = score_project(title, description, par_libraries)
    
    if evaluations:
        print("\n✅ SCORING SUCCESSFUL:")
        for ev in evaluations:
            print(f"   - {ev['consultant']}: {ev['score']}%")
        
        # 4. Log to DB
        log_evaluation(title, platform, evaluations)
        print("\n💾 Saved to DB. Check your Dashboard now!")
    else:
        print("\n❌ SCORING FAILED. Check logs above for Claude errors.")

    mail.logout()

if __name__ == "__main__":
    test_latest()
