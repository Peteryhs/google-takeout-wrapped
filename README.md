# Google Takeout Wrapped

A Python script that parses your Google Takeout data and generates a beautiful, interactive "Spotify Wrapped" style web dashboard. 

## 📦 Requirements

- Python 3.6+
- Your Google Takeout export

## 🚀 How to get your Google Takeout Data

1. Go to [Google Takeout](https://takeout.google.com/).
2. Select the following Google services (others are not currently supported):
   - **Drive**
   - **Mail**
   - **Google Chat**
   - **Classroom**
   - **My Activity** (Make sure Drive activity is included)
3. Export the archive as a `.zip` file.
4. Extract the `.zip` file to your computer. You should see a folder containing directories like `Drive`, `Mail`, `Google Chat`, etc.

## 🛠️ Usage

1. Open a terminal and navigate to the `src` directory of this project:
   ```bash
   cd google-takeout-wrapped/src
   ```

2. Run the `build.py` script. Pass the absolute path to your unzipped Takeout directory and your email/name so it can filter you out of the "Top Contacts" rankings.
   ```bash
   python3 build.py --takeout_dir "/path/to/your/Takeout" --user_email "your.email@gmail.com" --user_name "Your Name"
   ```

3. The script will process your data and generate a `dist` folder. 
4. **View locally:**
   ```bash
   python3 -m http.server 8080 -d dist
   ```
   Open `http://localhost:8080` in your browser.

## ☁️ Deploying to Cloudflare Pages (Optional)

You can easily host your dashboard for free using Cloudflare Pages!

1. Log in to [Cloudflare Pages](https://pages.cloudflare.com/).
2. Click **Create Application** -> **Pages** -> **Upload assets**.
3. Name your project and drag-and-drop your generated `dist` folder directly into the browser.
4. Click **Deploy**. Your Wrapped dashboard is now live!
