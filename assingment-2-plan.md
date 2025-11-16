# Requirements Overview

1. Code Quality and Testing
    -   Refactor your code to remove code smells (e.g. duplication, long methods, hardcoded values) and follow SOLID principles.
    -   Add automated unit and integration tests.
    -   Achieve at least 70% code coverage.
    -   Include a test report in your repo.
2. Continuous Integration (CI)
    -   Create a CI pipeline (more details about this to come)
    -   Pipeline must run tests, measure coverage, and build your application.
    -   The pipeline should fail if tests fail or coverage is below 70%.
3. Deployment Automation (CD)
    -   Containerize the app using Docker.
    -   Add a deployment step to a cloud platform (more details about this to come).
    -   Configure secrets and triggers so only the main branch deploys automatically.
4. Monitoring and Health Checks
    -   Add a /health endpoint returning basic app status.
    -   Expose metrics for request count, latency, and errors.
    -   Provide a minimal Prometheus or Grafana setup (config or screenshots).
5. Documentation
    -   Update README.md with clear run, test, and deploy instructions.
    -   Add a short REPORT.md summarizing what was improved and how.

# Steps

1. Review code, look for oppurtunities to implement design patterns and enforce SOLID principles
2. Implement health checks + monitoring
    -   grafana or prometheus??
    -   access control for monitoring?
3. Add some more tests and configure html coverage report
4. Look into GH actions, how to configure CI/CD stuff on it? How can it init an Azure deployment?
5. Deploy on azure, only after GH actions have been setup