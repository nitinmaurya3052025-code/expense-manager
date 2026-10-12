# Python Desktop Expense Tracker

A desktop-based expense tracking application built using Python, Tkinter,
TCP sockets, and MySQL. It allows users to record, view, edit, and delete
expenses through a graphical user interface.

## Features

- Add new expenses with amount, category, and description.
- View all recorded expenses in a table.
- Edit existing expenses.
- Delete selected expenses.
- View total expenses and transaction count.
- Visualize category-wise spending using a bar chart.
- Communicate between the client and server using TCP sockets.
- Store expense records in a MySQL database.
- Scroll through the dashboard using a vertical scrollbar.

## Technologies Used

- Python
- Tkinter — graphical user interface
- TCP Sockets — client-server communication
- MySQL — database
- Matplotlib — category-wise spending chart
- python-dotenv — environment variable management
- Git and GitHub — version control

## Project Structure

```text
python_version_expense-tracker/
├── add_expense.py
├── client.py
├── database.py
├── gui_client.py
├── server.py
├── .env.example
├── .gitignore
└── README.md
