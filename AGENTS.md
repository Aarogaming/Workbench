# Workbench Agent Guide

## Scope
This file defines default operating behavior for IDE agents working inside `Workbench` (development tools module).

## Primary Goals
1. Provide development and testing tools for the ecosystem
2. Maintain integration with Library federation contracts
3. Keep development workflows consistent and reproducible
4. Support continuous integration and testing

## Operating Principles
1. Workbench is a development tools subsystem within AaroneousAutomationSuite
2. All v1.0.0 governance rules apply (minimal dependencies, type-safe, deterministic)
3. Development tools must be non-breaking and version-compatible
4. Testability and CI/CD integration are core responsibilities

## Module Responsibilities
- Development environment setup and configuration
- CI/CD pipeline management
- Testing framework integration
- Tool compatibility and version management
- Integration with Guild and Library through federation contracts

## Validation Requirements
Before committing changes:
1. Verify development workflows still function
2. Test CI/CD pipeline integration
3. Confirm test framework compatibility
4. Validate federation contract compatibility
5. Document tool updates and version changes

## Version Control
- Repository: `https://github.com/Aarogaming/Workbench.git`
- Current Version: v1.0.0
- Default Branch: `main`
- Role: Development Tools Module

## Federation Integration
Workbench integrates with federation through:
- Library discovery contracts for artifact discovery
- Guild CI triage for test result synchronization
- AaroneousAutomationSuite orchestration

## Known Constraints
- Development tools must not interfere with production operations
- CI/CD changes require testing before deployment
- Tool compatibility must be maintained across versions
- Testing patterns must be consistent with Guild standards

## Support & Escalation
- Development tool issues: Handle locally
- Federation integration: Escalate to Library
- CI/CD pipeline issues: Escalate to AaroneousAutomationSuite
- Test framework compatibility: Coordinate with Guild

---

*This guide was created as part of the v1.0.0 production release.*
