from datetime import datetime, timezone

now_utc = datetime.now(timezone.utc)
print(now_utc)
print(now_utc.tzinfo)  # UT
now_utc = datetime.now()
print(now_utc)
print(now_utc.tzinfo)  # UTC