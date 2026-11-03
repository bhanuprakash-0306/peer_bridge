# PeerBridge — Student Skill Exchange Platform

A beginner-friendly Streamlit + SQLite MVP for students to exchange skills without necessarily paying for tutoring.

## Features
- Student registration and directory
- Add skills students can teach or want to learn
- Search for peer matches
- Post learning requests
- Schedule learning sessions
- Leave ratings and reviews
- SQLite database created automatically

## Requirements
- Python 3.10 or newer
- VS Code
- Internet connection for installing Streamlit

## Run on Windows (VS Code terminal)

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If `py` does not work, use `python` instead.

## Suggested demo
1. Register two students, for example Asha (Cyber Security) and Ravi (CSE).
2. Add Ravi's skill: `Java basics` → `Can teach`.
3. Add Asha's skill: `Java basics` → `Wants to learn`.
4. Use Explore & Match to search for Java basics.
5. Post a request, schedule a session, then leave a review.

## Project structure
```text
peer_bridge/
├── app.py
├── database.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Database tables
- `students`
- `skills`
- `requests`
- `sessions`
- `reviews`

## Notes
This is an educational MVP. It does not yet include authentication, private messaging, email verification, or deployment configuration. Do not enter sensitive personal information.
