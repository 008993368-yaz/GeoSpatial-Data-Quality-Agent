# Sprint 1 - Project Foundation

> **Sprint Number:** Sprint 1  
> **Sprint Goal:** Establish development environment and basic project infrastructure  
> **Duration:** Week 1 (2 weeks)  
> **Team Capacity:** 40 story points

---

## Sprint Planning

### Sprint Goal
Set up complete development environment for both frontend and backend, including Docker containerization and CI/CD pipeline. By the end of this sprint, the team should be able to run the application locally and have automated testing in place.

### Team Members
| Name | Role | Capacity (hours) | Availability |
|------|------|-----------------|--------------|
| Backend Dev | Backend Developer | 40h | 100% |
| Frontend Dev | Frontend Developer | 40h | 100% |
| DevOps | DevOps Engineer | 20h | 50% |

### Velocity
- **Previous Sprint Velocity:** N/A (First sprint)
- **Planned Velocity:** 40 points
- **Confidence Level:** Medium

---

## Selected Backlog Items

### High Priority (Must Complete)

#### BACK-1: Initialize Backend Project Structure
- **Story Points:** 3
- **Assignee:** Backend Dev
- **Dependencies:** None
- **Status:** ⬜ Not Started

**Sprint Tasks:**
- [ ] Create backend directory structure
- [ ] Set up Python virtual environment
- [ ] Create requirements.txt with core dependencies
- [ ] Create .env.example template
- [ ] Set up basic logging
- [ ] Create main.py with FastAPI app
- [ ] Verify server starts successfully
- [ ] Document setup process

**Acceptance Criteria:**
- [ ] Backend directory exists with proper structure
- [ ] requirements.txt includes all Phase 1 dependencies
- [ ] Server starts without errors on port 8000
- [ ] Basic health check endpoint responds
- [ ] README updated with backend setup instructions

---

#### BACK-2: Initialize Frontend Project Structure
- **Story Points:** 3
- **Assignee:** Frontend Dev
- **Dependencies:** None
- **Status:** ⬜ Not Started

**Sprint Tasks:**
- [ ] Create frontend directory using Vite
- [ ] Install React, TypeScript, and core dependencies
- [ ] Install Calcite components
- [ ] Configure TypeScript strict mode
- [ ] Set up ESLint and Prettier
- [ ] Create .env.example template
- [ ] Create basic App component
- [ ] Verify dev server runs
- [ ] Configure path aliases

**Acceptance Criteria:**
- [ ] Frontend directory exists with Vite setup
- [ ] All core dependencies installed
- [ ] Dev server runs on port 5173
- [ ] TypeScript compiles without errors
- [ ] ESLint configuration working
- [ ] README updated with frontend setup instructions

---

#### BACK-3: Set Up Docker Environment
- **Story Points:** 5
- **Assignee:** DevOps
- **Dependencies:** BACK-1, BACK-2
- **Status:** ⬜ Not Started

**Sprint Tasks:**
- [ ] Create Dockerfile.backend
- [ ] Create Dockerfile.frontend
- [ ] Create docker-compose.yml
- [ ] Create .dockerignore files
- [ ] Test Docker build process
- [ ] Test docker-compose up
- [ ] Document Docker usage
- [ ] Troubleshoot any issues

**Acceptance Criteria:**
- [ ] Dockerfile.backend builds successfully
- [ ] Dockerfile.frontend builds successfully
- [ ] docker-compose.yml orchestrates both services
- [ ] Backend accessible at localhost:8000
- [ ] Frontend accessible at localhost:5173
- [ ] Volume mounts working for live reload
- [ ] Documentation includes Docker commands

---

#### BACK-4: Configure CI/CD Pipeline
- **Story Points:** 5
- **Assignee:** DevOps
- **Dependencies:** BACK-1, BACK-2
- **Status:** ⬜ Not Started

**Sprint Tasks:**
- [ ] Create .github/workflows/backend-ci.yml
- [ ] Configure Python linting (black, flake8)
- [ ] Set up pytest in CI
- [ ] Create .github/workflows/frontend-ci.yml
- [ ] Configure ESLint in CI
- [ ] Set up TypeScript checking
- [ ] Test CI pipeline with sample PR
- [ ] Configure branch protection

**Acceptance Criteria:**
- [ ] Backend CI runs on push and PR
- [ ] Backend linting checks pass
- [ ] Frontend CI runs on push and PR
- [ ] Frontend linting checks pass
- [ ] TypeScript type checking works
- [ ] Branch protection configured for main
- [ ] CI status badges added to README

---

### Medium Priority (Should Complete)

#### BACK-5: Implement File Upload API
- **Story Points:** 5
- **Assignee:** Backend Dev
- **Dependencies:** BACK-1
- **Status:** ⬜ Not Started

**Sprint Tasks:**
- [ ] Create upload endpoint POST /api/v1/upload
- [ ] Implement file validation (type, size)
- [ ] Create uploads directory structure
- [ ] Generate unique dataset IDs
- [ ] Extract basic file metadata
- [ ] Implement error handling
- [ ] Write unit tests
- [ ] Document API endpoint

**Acceptance Criteria:**
- [ ] Endpoint accepts multipart/form-data
- [ ] Supports .shp, .geojson, .kml, .csv files
- [ ] Validates file size (max 50MB)
- [ ] Returns dataset info with UUID
- [ ] Proper error responses for invalid files
- [ ] Unit tests cover happy path and errors
- [ ] OpenAPI/Swagger docs updated

---

#### BACK-16: Create Application Shell
- **Story Points:** 5
- **Assignee:** Frontend Dev
- **Dependencies:** BACK-2
- **Status:** ⬜ Not Started

**Sprint Tasks:**
- [ ] Create App.tsx with Calcite Shell
- [ ] Add Calcite Shell Panel
- [ ] Implement header component
- [ ] Add footer with version
- [ ] Configure responsive layout
- [ ] Add theme toggle
- [ ] Test on different screen sizes
- [ ] Write component tests

**Acceptance Criteria:**
- [ ] Application shell renders correctly
- [ ] Header includes title and navigation
- [ ] Footer displays version info
- [ ] Layout responsive on mobile/tablet/desktop
- [ ] Theme toggle works (light/dark)
- [ ] No console errors
- [ ] Component tests pass

---

### Stretch Goals (Nice to Have)

#### BACK-17: Create File Upload Component
- **Story Points:** 5
- **Assignee:** Frontend Dev
- **Dependencies:** BACK-16
- **Status:** ⬜ Not Started

**Sprint Tasks:**
- [ ] Create FileUploader.tsx component
- [ ] Implement drag-and-drop
- [ ] Add file input button
- [ ] Display file information
- [ ] Show upload progress
- [ ] Add client-side validation
- [ ] Display error/success messages
- [ ] Write component tests

**Acceptance Criteria:**
- [ ] Drag-and-drop zone works
- [ ] File input button functional
- [ ] Shows file name, size, type
- [ ] Progress bar displays during upload
- [ ] Validates file type on client
- [ ] Error messages are clear
- [ ] Success confirmation shown
- [ ] Accessible with keyboard

---

## Daily Standups

### Day 1 - [Date TBD]
**Completed:**
- Sprint planning meeting
- Environment setup begun

**In Progress:**
- BACK-1: Backend structure
- BACK-2: Frontend structure

**Blockers:**
- None

---

### Day 2 - [Date TBD]
**Completed:**
- 

**In Progress:**
- 

**Blockers:**
- 

---

### Day 3 - [Date TBD]
**Completed:**
- 

**In Progress:**
- 

**Blockers:**
- 

---

### Day 4 - [Date TBD]
**Completed:**
- 

**In Progress:**
- 

**Blockers:**
- 

---

### Day 5 - [Date TBD]
**Completed:**
- 

**In Progress:**
- 

**Blockers:**
- 

---

## Mid-Sprint Check-in (Day 5)

**Progress:**
- Story points completed: [X/40]
- Items done: [X/7]

**Risks:**
- 

**Adjustments:**
- 

---

## Sprint Review

### Demo Items
- [ ] BACK-1: Backend running locally and in Docker
- [ ] BACK-2: Frontend running locally and in Docker
- [ ] BACK-3: Full stack running via docker-compose
- [ ] BACK-4: CI/CD pipeline executing successfully
- [ ] BACK-5: File upload API working
- [ ] BACK-16: Application shell displaying

### Stakeholder Feedback
- 

---

## Sprint Retrospective

### What Went Well
- 

### What Could Be Improved
- 

### Action Items
- [ ] 

### Metrics
- **Completed Story Points:** [X]
- **Planned Points:** 40
- **Velocity:** [X]
- **Completion Rate:** [X%]
- **Carryover Items:** [N]

---

## Notes
- First sprint focused on infrastructure
- Team establishing working rhythm
- Docker environment critical for consistent development
- CI/CD will enable faster iterations in future sprints
