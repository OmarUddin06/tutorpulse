# TutorPulse Model Monitoring Plan

## Purpose

This document defines the monitoring foundations for the TutorPulse support-risk inference service.

The current project is a portfolio demonstration using synthetic data. It does not operate a real production monitoring platform.

The plan distinguishes between:

- monitoring signals already emitted by the application;
- metrics that can be derived from those signals;
- outcome monitoring that would require later verified results;
- governance actions when a problem is detected.

Monitoring must not turn the model into an automatic decision-maker.

## Monitoring principles

TutorPulse monitoring follows these principles:

1. protect learner privacy;
2. separate service health from model readiness;
3. monitor errors as well as successful predictions;
4. use aggregate measures wherever possible;
5. compare current behaviour with an approved baseline;
6. investigate changes before modifying the model;
7. retain human review;
8. never retrain or change thresholds automatically.

## Health endpoints

TutorPulse provides two different health checks.

### Application health

```http
GET /health