# 🛠️ Mechanic API  
### Because even your backend needs regular service... and maybe therapy.

Welcome to the **Mechanic API**, a Flask-powered backend I built for managing customers, mechanics, inventory, and service tickets — and for testing my patience, sanity, and ability to keep a CI pipeline alive longer than my houseplants.

---

## 🚗 What This API Does (When It's Not in a Mood)

- Manages **customers**, **mechanics**, **inventory**, and **service tickets**
- Full **JWT auth** because I'm all about keeping things 🔐  
- **Rate limiting** because bots are wild and need chill  
- Includes **Swagger UI** that took longer to show up than my Amazon Prime delivery  
- Modularized with Flask blueprints because I enjoy pain in organized layers

---

## 💪 What I Actually Got Working

- ✅ Multi-blueprint Flask app with full CRUD routes  
- ✅ Working CI/CD pipeline that deploys to Render without emotional blackmail  
- ✅ Unit tests with `unittest` (and one intentionally failing test just to keep it spicy)  
- ✅ Swagger docs at `/apidocs` after **hours** of tweaking `static_url_path`, templates, configs, and my attitude  
- ✅ Token-based login for customers and mechanics that will absolutely judge you if you don’t send the right headers

---

## 😤 Real Frustrations I Faced

- **GitHub Actions** said “exit code 1” like it was my job title  
- Render said “✅ Build successful” while Swagger said “404 Not Found. Try harder.”  
- Accidentally redeployed 6 times between 2:00am and 3:30am chasing a config typo  
- Flasgger documentation might’ve been written by a cryptic AI trained on sarcasm  
- "ModuleNotFoundError: testing" made me question every folder, file, and life choice  
- At one point I thought *maybe* the server was haunted. It wasn’t. But I had hope.

---

## 😅 Some Memorable Moments

- I literally had a test fail because the error message said `"Name and price required."` instead of `"Missing"`. Yes, it worked. But also no, it failed.
- Swagger UI refused to load because it didn’t like the way I defined `static_url_path`. *Same, Swagger. Same.*
- Render: “Your service is live.”  
  Me, refreshing for the 17th time: “Where tho?”

---

## 🧪 Testing

To run the tests (and maybe break your spirit):

```bash
python -m unittest discover -s tests
```

You’ll get green dots unless you hit the one I left in to fail on purpose. You’re welcome.

---

## 🔄 CI/CD Setup

CI/CD is powered by:
- GitHub Actions (because if I can automate crying, I will)
- Render deployment (free tier... which spins down constantly like it's playing hard to get)

### CI Steps:
1. ✅ **Build**  
2. 🧪 **Run Tests**  
3. 🚀 **Deploy to Render (hopefully)**

If it fails? I stare into the logs and wonder why I didn't just go into pottery.

---

## 📜 Live API Docs

They exist now. I swear.  

🔗 [https://mechanic-api-ewyr.onrender.com/apidocs](https://mechanic-api-ewyr.onrender.com/apidocs)

Yes, this used to return a blank screen. Yes, I fixed it. Yes, it took way too long.

---

## 🧰 Tech Stack

- **Flask** (plus Blueprints)
- **SQLAlchemy + Marshmallow**
- **JWT auth** via `python-jose`
- **Flasgger** (the sassiest Swagger wrapper ever)
- **SQLite** (because I like living dangerously)
- **CI/CD** with GitHub Actions & Render

---

## 🧠 Things I Learned the Hard Way

- Don’t forget to add `__init__.py` to your folders, or Flask will act like they don’t exist.
- Swagger will load nothing if you forget `static_folder`. Nothing. No error. Just *vibes*.
- YAML cares deeply about indentation. Like... passive-aggressively deeply.
- “Tests passing locally” means nothing to CI. CI wants blood.
- Sometimes fixing the API means fixing *your expectations*.

---

## 🧊 Final Thoughts

This was meant to be a simple project. It became a quest.  
I fought CI dragons, tamed Render demons, and learned that `'exit code 1'` is GitHub's way of saying *"get good."*

But I made it. Swagger works. Tests pass. CI/CD flows. And somewhere in all that chaos… I became better.

So if you're reading this:
- Be proud of your bugs.
- Laugh at your logs.
- And never let Swagger break your swagger.

---