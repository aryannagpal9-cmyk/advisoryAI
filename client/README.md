# AdvisoryAI Frontend (Dashboard)

A premium, high-density React application designed for financial advisors to monitor and manage autonomous client/provider chases. Built with a focus on visual clarity and real-time observability.

## 🎨 Design System: "Stealth Grey"

The application employs a custom monochromatic dark theme defined via Tailwind CSS. This "Stealth Grey" aesthetic minimizes visual fatigue while highlighting critical exceptions.

- **Background**: `#0a0a0a` (Neutral 950) - Deep, obsidian surface.
- **Surface**: `#171717` (Neutral 900) - Card and sidebar backgrounds.
- **Contrast**: `#fafafa` (Neutral 50) - Primary text and high-contrast actions.
- **Glassmorphism**: Subtle frosted glass effects (via `backdrop-blur`) for overlays and navigation elements.

## 🧱 Component Architecture

### View Controllers
- **Dashboard**: The nerve center. Displays global volume, automation efficiency, and the "Priority Focus" section.
- **Case Explorer**: High-density table for searching and filtering active cases.
- **Case Details**: Vertical timeline of audit logs and granular request management.
- **Exception Feed**: Real-time ticker for items requiring immediate human judgment (Escalations, Invalid Docs).

### Core UI Components
- **Automation Gauge**: Visual indicator of the ratio of automated vs. manual task completions.
- **Audit Trail**: Step-by-step history of agent and advisor actions for a specific case.
- **Magic Modal**: Context-aware dialogs for case creation and request overrides.

## ⚡️ Tech Stack

- **React 18**: Component-based UI logic.
- **Vite**: Ultra-fast development environment and optimized production builds.
- **Tailwind CSS**: Utility-first styling with a custom theme extension.
- **Lucide React**: Minimalist, consistent iconography.

## 🚀 Setup & Development

1. **Installation**:
   ```bash
   cd client
   npm install
   ```

2. **Environment**:
   Copy the example environment file:
   ```bash
   cp .env.example .env
   # Usually defaults to http://localhost:8000 for the VITE_API_URL
   ```

3. **Execution**:
   ```bash
   npm run dev
   ```
   The dashboard will be available at `http://localhost:5173`.

4. **Production Build**:
   ```bash
   npm run build
   ```
   Static assets are generated in the `dist/` directory.
