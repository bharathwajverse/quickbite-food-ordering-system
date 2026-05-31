# QuickBite

A Python desktop food ordering system built with Tkinter and SQLite.

## Overview

QuickBite is a local restaurant ordering application with:
- user authentication (admin and customer)
- menu browsing and cart management
- order checkout and order history
- review submission
- admin analytics and coupon management
- data export support

## Features

- Login and registration for users
- Menu browsing with categories, stock tracking, and item images
- Add items to cart, apply coupons, and place orders
- Track order history and read/write reviews
- Admin dashboards for sales reports, coupon management, and analytics
- SQLite database persistence in `quickbite.db`

## Requirements

- Python 3.10+ (Tkinter included with standard Python installs)
- `requests` Python package

## Installation

From the project root:

```bash
python -m pip install -r requirements.txt
```

## Run the app

From the project root:

```bash
python main_gui.py
```

## Project structure

- `main_gui.py` - application entry point
- `db.py` - database initialization and connection utilities
- `auth_view.py`, `menu_view.py`, `cart_view.py`, `review_view.py`, `orders_view.py`, `admin_view.py` - UI views
- `styles.py` - shared UI styling constants
- `export_data.py` - CSV export helper
- `check_db.py` - database validation utilities
- `assets/` - image assets used by the GUI
- `quickbite.db` - local SQLite database file (generated automatically)

## Notes

- The database file `quickbite.db` is created automatically when the app runs.
- Admin credentials are seeded by default as:
  - username: `admin`
  - password: `admin123`

## License

This project is available under the MIT License.
