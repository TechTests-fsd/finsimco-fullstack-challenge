# FinSimCo - Full-Stack Coding Challenge

This repository contains my solution for the FinSimCo coding challenge. It's a full-stack application featuring a Python backend for a CLI-based simulation and a React frontend for a UI-based simulation.

The primary focus of this project was not just to deliver functionality, but to showcase a professional, maintainable, and scalable codebase, as requested in the challenge description.


---

## ✨ Core Features

*   **Two Complete Simulations:** Both the backend CLI (Game 1 & 2) and the frontend UI challenges have been implemented.
*   **Clean Architecture (Backend):** The Python backend is built using Clean Architecture principles, ensuring a strict separation between domain logic, application use cases, and infrastructure.
*   **Domain-Driven Design (Backend):** The core logic is modeled with rich domain entities and value objects, making the business rules explicit and robust.
*   **Real-Time CLI (Backend):** The CLI for Game 1 uses `gevent` for cooperative multitasking, providing a live-updating view without blocking user input.
*   **Modern Frontend:** A visually appealing and user-friendly interface built with React, TypeScript, and Tailwind CSS, based on the provided mockups and my own UX enhancements.
*   **Data-Driven Configuration:** All game rules, terms, and validation logic are centralized in a single configuration service, making the system easy to modify and extend.

---

## 🛠️ Tech Stack

*   **Backend:** Python, Gevent, SQLAlchemy Core, PostgreSQL, Redis, Pydantic, `dependency-injector`.
*   **Frontend:** React, TypeScript, Vite, Zustand, Tailwind CSS, `lucide-react`.
*   **Tooling:** Git

---

## 🚀 Backend: Setup & Usage

The backend is a CLI application that runs two separate games.

### Prerequisites

*   Python 3.10+
*   PostgreSQL 12+ (running locally)
*   Redis (running locally)

### 1. Database Setup

You'll need a dedicated user and database. Connect to your PostgreSQL instance (e.g., with `psql`) and run:

```sql
CREATE DATABASE finsimco;
CREATE USER finsimco_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE finsimco TO finsimco_user;
```
*Note: On macOS with Homebrew, you might need to create the `postgres` superuser role first if it doesn't exist (`CREATE ROLE postgres WITH LOGIN PASSWORD 'password' SUPERUSER;`).*

### 2. Environment Configuration

Navigate to the `/backend` directory. Create a `.env` file by copying `.env.example` and fill in your connection details.

```env
# .env
DATABASE_URL=postgresql://finsimco_user:your_password@localhost:5432/finsimco
REDIS_URL=redis://localhost:6379/0
```

### 3. Installation

```bash
# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Initialize Database Schema

This command will create all the necessary tables in your database.

```bash
python run.py --init-db
```

### 5. Running the Simulations

Open two separate terminals. In each, navigate to the `backend` directory and activate the virtual environment (`source venv/bin/activate`).

**Game 1 (Valuation):**

*   **Terminal 1 (Team 1):**
    ```bash
    python run.py --team 1 --game 1
    ```
*   **Terminal 2 (Team 2):**
    ```bash
    # Get the session ID from Terminal 1's output
    python run.py --team 2 --game 1 --session <SESSION_ID_FROM_TEAM_1>
    ```

**Game 2 (Company Trading):**

*   **Terminal 1 (Team 1 - Pricing):**
    ```bash
    python run.py --team 1 --game 2
    ```
*   **Terminal 2 (Team 2 - Bidding):**
    ```bash
    python run.py --team 2 --game 2 --session <SESSION_ID_FROM_TEAM_1>
    ```

---

## 🎨 Frontend: Setup & Usage

The frontend is a standalone React application.

### Installation

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install
```

### Running the Development Server

```bash
npm run dev
```
This will start the Vite development server, typically at `http://localhost:5173`. The application has two pages: `/team1` and `/team2`, which can be accessed from the home page.

---

## 🏗️ Architectural Notes & Design Decisions

This project was an exercise in building robust, maintainable software. Here are some key decisions:

1.  **Clean Architecture (Backend):** The strict separation of layers was the highest priority. The Domain layer has zero external dependencies, making it easy to test and reason about. The Application layer orchestrates use cases, and the Infrastructure layer handles all the "dirty" work (DB, Redis).

2.  **Unit of Work & DTOs:** I encountered the classic `This transaction is inactive` error from SQLAlchemy. Instead of a quick fix, I implemented a full DTO (Data Transfer Object) pattern. The `GameService` now fetches all data within a single transaction, maps it to clean DTOs, and returns those to the presentation layer. This completely decouples the UI from any ORM session state and is a robust solution for this common problem.

3.  **Data-Driven Design:** All game rules, terms, validation parameters, and even UI text like role descriptions are centralized in `GameConfiguration.py`. This means to change a game's behavior or add a new one, you primarily edit this one config file, rather than hunting through business logic in services.

4.  **Resolving Ambiguous Requirements (Game 2):** I chose to implement the version described in the `Backend Challenge.xlsx` file as it was the more detailed technical artifact. I then designed a new approval flow (`finalize -> approve`) to satisfy the "same logic of execution" requirement in a way that made sense for that game's mechanics. 

5.  **Pragmatic Frontend:** The frontend UI was built from scratch without a component library, as requested. I focused on creating a small, reusable UI kit (`Button`, `Input`, `Slider`, `Tooltip`) and a clean, reactive state management system with Zustand.

---

## 💡 Potential Improvements

Given more time, here's what I'd do next:

*   **Testing:** The architecture is highly testable, but a test suite was not implemented to focus on the core task. The strategy would be:
    *   **Unit Tests (pytest):** For the Domain layer and pure services (`ValuationCalculator`, `Game2AnalyticsService`).
    *   **Integration Tests:** For repositories against a test database.
    *   **E2E Tests:** For the CLI, simulating two processes.
*   **Repository `save` Logic:** The current `save` methods use a `SELECT` then `UPDATE/INSERT` pattern. For production, I would refactor this to use a database-specific `UPSERT` (`INSERT ... ON CONFLICT DO UPDATE` for PostgreSQL) for better performance and atomicity.
*   **Frontend Responsiveness:** The frontend has basic responsiveness (`lg:` breakpoints), but I would add more granular control for a perfect experience on tablets and smaller devices.