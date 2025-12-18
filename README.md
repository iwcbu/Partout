# Partout

CS412 Final Project (Boston University): a full stack Django marketplace for the car community; built for buying/selling parts, connecting with other drivers, and managing your own “garage” profile.

**Live demo:** https://cs-webapps.bu.edu/iwc3/partout/market

**[Open Partout Project Folder](https://github.com/iwcbu/cs412-private/tree/main/partout)**

---

## What Partout Does

Partout is a community-first marketplace where users can:
- Create an authenticated **Driver profile** (bio, location, profile image)
- Build a personal **Garage** by adding cars (make/model/year + structured attributes like drivetrain/style)
- Post **Listings** for automotive parts tied to a car + seller, with listing status (Active/Pending/Sold)
- Browse the **Market feed** with pagination and search/filtering for active listings
- Submit **Offers** on listings and manage offer status (pending/accepted/declined)
- Start **Direct Messages** (conversations) and send messages between drivers (optionally tied to a listing)
- Use social signals: **Follow/Unfollow**, **Like/Unlike**, **Save/Unsave** listings
- Leave **Ratings** for other drivers (stars + optional comment)

---

## Tech Stack

- **Backend:** Django (Python), Django ORM
- **Views:** Django class-based views (ListView/DetailView/CreateView/UpdateView/DeleteView)
- **Auth:** Django built-in authentication (login/logout)
- **Media:** Image uploads for profiles/listings (commonly via Pillow)

---

## Key Features

### Marketplace
- Market page showing active listings, optimized queries (select-related seller/car) and paginated results
- Listing detail pages + CRUD for sellers

### Messaging
- Conversation based direct messages between drivers
- Messages include sender/receiver and text content
- Conversations can optionally be linked to a specific listing

### Offers & Negotiation
- Buyers can create offers for listings
- Sellers can accept or delete offers

### Community
- Follow relationships between drivers
- Likes and save interactions on listings by drivers
- Driver ratings with optional comments

---

## Local Setup (generic Django)

```bash
# 1) Create & activate a virtualenv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2) Install deps
pip install django pillow

# 3) Migrate + run
python manage.py migrate
python manage.py runserver
