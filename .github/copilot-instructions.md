<!-- Copilot instructions for the GoExplorer repo -->
# Repository guidance for AI coding agents

Purpose: quick, actionable notes to help an AI agent make safe, correct changes in this Django app.

- Big picture
  - Django 4.x monolith handling hotel listings, room types, date availability and bookings.
  - Single app: `booking` (models, templates, REST endpoints). Project settings in `core/settings.py`.
  - Local dev uses SQLite and local `media/` storage (see `MEDIA_ROOT` in `core/settings.py`).

- Key files and where to make common changes
  - Models: `booking/models.py` — Hotel, HotelImage (`related_name='images'`), RoomType, RoomPlan (`related_name='plans'`), Booking.
  - Templates: `booking/templates/booking/room_list.html` (room card + plans), `booking/templates/booking/base.html` (layout).
  - Static: `booking/static/booking/css/main.css` (primary layout & styles), `booking/static/booking/js/gallery.js` (thumbnail strip, lightbox, play/pause logic).
  - Settings: `core/settings.py` — JWT auth, Razorpay test keys, `EMAIL_BACKEND` set to console in dev.

- UI patterns to preserve
  - Gallery/Lightbox: thumbnail strip (`.thumb-strip`) is the primary control. Large slider is hidden; lightbox overlay implemented in `gallery.js` (classes: `.lb-overlay`, `.lb-img`, `.play-btn`).
  - Room plans: templates use `.plans-container` wrapping `.plan-grid` and `.plan-box`. CSS expects centered plan boxes inside a right-side card (`.room-right`).
  - When editing templates or CSS, keep the `.plans-container` structure to preserve the card layout.

- Important conventions & gotchas
  - `HotelImage.is_primary` logic unsets other primary images in `save()` — be careful when changing image selection behavior.
  - `RoomType.price` exists as a legacy DB column (`db_column='price'`) — migration history relies on it. Don't remove or rename without migrating carefully.
  - Templates rely on `django.template.context_processors.request` in `TEMPLATES` (see comment in `core/settings.py`). That is required for admin & some template helpers.

- Developer workflows (commands)
  - Setup (dev):
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver
    ```
  - Run checks/tests:
    ```bash
    python manage.py check
    python manage.py test
    ```
  - When changing media or images locally, files are stored under `media/` (ignored by `.gitignore`).

- Integrations
  - Razorpay: test keys in `core/settings.py`. Webhook secret present as `RAZORPAY_WEBHOOK_SECRET`.
  - REST: `rest_framework_simplejwt` used for auth (see `REST_FRAMEWORK` in settings). Many API endpoints expect Bearer JWT.

- Repo maintenance notes
  - `.gitignore` should include `__pycache__/`, `*.pyc`, `.venv/`, `db.sqlite3` and `media/` (this repo already added a `.gitignore`).
  - Migrations are currently committed under `booking/migrations/`. Do not remove them without explicit instruction — removing migrations will break fresh setup for contributors.

- Quick examples (where to change things)
  - To change plan card layout: edit `booking/templates/booking/room_list.html` (the `.plans-container` block) and `booking/static/booking/css/main.css` (`.plans-container`, `.plan-grid`, `.plan-box`).
  - To adjust gallery behavior (autoplay, button placement): edit `booking/static/booking/js/gallery.js` and preserve `.thumb-strip` interactions.

If anything is unclear or you want stricter rules (for example: always open a PR, run tests, or a specific linting/format step), say so and I'll update this file.
