import streamlit as st
import instaloader
import time
import random
import pandas as pd
import os

st.title("📸 Instagram Profile Scraper")

username = st.text_input("Enter your Instagram username:")
password = st.text_input("Enter your Instagram password:", type="password")
target_username = st.text_input("Enter the target Instagram username to scrape:")

if st.button("Start Extraction"):
    if not username or not password or not target_username:
        st.error("Please fill all fields to proceed.")
    else:
        L = instaloader.Instaloader()
        csv_filename = f"{target_username}_profile_data.csv"
        extraction_stopped = False

        try:
            L.login(username, password)
        except Exception as e:
            st.error(f"❌ Login failed: {e}")
            st.stop()

        delay = random.randint(3, 10)
        st.info(f"⏳ Waiting {delay}s before fetching profile...")
        time.sleep(delay)

        try:
            profile = instaloader.Profile.from_username(L.context, target_username)
        except Exception as e:
            st.error(f"❌ Failed to load profile: {e}")
            st.stop()

        followers = []
        followees = []

        st.info("📥 Fetching up to 30 followers...")
        try:
            for i, follower in enumerate(profile.get_followers()):
                followers.append(follower.username)
                st.write(f"  ➕ {follower.username}")
                if i >= 29:
                    break
                delay = random.randint(3, 10)
                time.sleep(delay)
        except Exception as e:
            st.warning(f"⚠️ Error during follower fetch: {e}")
            extraction_stopped = True

        st.info("💾 Saving partial followers to CSV...")
        try:
            partial_info = {
                "Username": profile.username,
                "Followers Usernames": ", ".join(followers),
            }
            pd.DataFrame([partial_info]).to_csv(csv_filename, index=False)
        except Exception as e:
            st.error(f"❌ Failed to write partial followers to CSV: {e}")

        if not extraction_stopped:
            delay = random.randint(5, 15)
            st.info(f"⏳ Waiting {delay}s before fetching followees...")
            time.sleep(delay)

            st.info("📥 Fetching up to 30 followees...")
            try:
                for i, followee in enumerate(profile.get_followees()):
                    followees.append(followee.username)
                    st.write(f"  ➕ {followee.username}")
                    if i >= 29:
                        break
                    delay = random.randint(3, 10)
                    time.sleep(delay)
            except Exception as e:
                st.warning(f"⚠️ Error during followee fetch: {e}")
                extraction_stopped = True

        st.info("💾 Final save to CSV...")
        try:
            profile_info = {
                "Username": profile.username,
                "Full Name": profile.full_name,
                "Bio": profile.biography,
                "External URL (Bio Link)": profile.external_url,
                "Followers Count": profile.followers,
                "Following Count": profile.followees,
                "Post Count": profile.mediacount,
                "Is Verified": profile.is_verified,
                "Is Private": profile.is_private,
                "Is Business Account": profile.is_business_account,
                "Followers Usernames": ", ".join(followers),
                "Following Usernames": ", ".join(followees),
            }
            pd.DataFrame([profile_info]).to_csv(csv_filename, index=False)
            st.success(f"✅ Profile data saved to '{csv_filename}'")
        except Exception as e:
            st.error(f"❌ Failed to save final CSV: {e}")

        if extraction_stopped:
            st.warning("🚫 Extraction Stopped due to an error or Instagram flag.")

        with open(csv_filename, "rb") as f:
            st.download_button("⬇️ Download Extracted CSV", f, file_name=csv_filename, mime="text/csv")