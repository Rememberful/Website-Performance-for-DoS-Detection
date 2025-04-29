import time
import requests
import matplotlib.pyplot as plt
from collections import Counter

# ====== Telegram Config ======
TELEGRAM_BOT_TOKEN = '7902712032:AAFDD6zWYpbqegcqVyzXewmQ3Yra0M4rmCE'
TELEGRAM_CHAT_ID = '7413356774'

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print("⚠️ Failed to send Telegram alert.")
    except Exception as e:
        print(f"⚠️ Telegram alert error: {e}")

def check_website(url, attempts=10, timeout_threshold=5, error_rate_threshold=0.5):
    timeouts = 0
    errors = 0
    total_time = 0
    response_times = []
    status_codes = []

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
    }

    print(f"Checking {url} for potential DoS attack symptoms...\n")

    for i in range(attempts):
        try:
            start = time.time()
            response = requests.get(url, timeout=timeout_threshold, headers=headers)
            elapsed = time.time() - start
            total_time += elapsed
            response_times.append(elapsed)
            status_codes.append(response.status_code)

            print(f"Attempt {i+1}: Status {response.status_code} in {elapsed:.2f} seconds")

            if response.status_code >= 500:
                errors += 1

        except requests.exceptions.Timeout:
            print(f"Attempt {i+1}: Timed out (> {timeout_threshold}s)")
            timeouts += 1
            response_times.append(timeout_threshold)
            status_codes.append('Timeout')
        except requests.exceptions.RequestException as e:
            print(f"Attempt {i+1}: Error - {e}")
            errors += 1
            response_times.append(0)
            status_codes.append('Error')

        time.sleep(1)

    avg_response_time = total_time / (attempts - timeouts) if (attempts - timeouts) else float('inf')
    error_rate = (errors + timeouts) / attempts

    print("\n--- Summary ---")
    print(f"Average response time: {avg_response_time:.2f} seconds")
    print(f"Error rate: {error_rate * 100:.1f}%")

    status_counts = Counter(status_codes)
    print("Status code breakdown:")
    for code, count in status_counts.items():
        print(f"  {code}: {count} times")

    if avg_response_time > 3 or error_rate > error_rate_threshold:
        alert_message = (
            f"⚠️ ALERT: Potential DoS detected on {url}\n"
            f"Average response time: {avg_response_time:.2f}s\n"
            f"Error rate: {error_rate * 100:.1f}%\n"
            f"Status breakdown: {dict(status_counts)}"
        )
        send_telegram_alert(alert_message)
        print("\n⚠️ WARNING: The website may be under a DoS attack or experiencing serious issues.")
    else:
        print("\n✅ The website appears normal.")

    # Plotting response times
    try:
        plt.figure(figsize=(10, 5))
        plt.plot(range(1, attempts + 1), response_times, marker='o', linestyle='-')
        plt.title(f"Response Time per Attempt for {url}")
        plt.xlabel("Attempt Number")
        plt.ylabel("Response Time (seconds)")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"⚠️ Unable to plot graph: {e}")

# Example usage
if __name__ == "__main__":
    url_to_check = input("Enter the website URL (include http/https): ")
    
    # Run continuously with a 10-minute delay between checks
    while True:
        check_website(url_to_check)
        print("\nWaiting 10 minutes before next check...")
        time.sleep(600)  # 600 seconds = 10 minutes
