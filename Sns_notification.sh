#!/usr/bin/bash

TOPIC_ARN="arn:aws:sns:us-east-1:145295581730:deployPortfolioTopic"
SUBJECT="Test message"
MESSAGE="This is only a test"

aws sns publish --topic-arn "$TOPIC_ARN" --subject "$SUBJECT" --message "$MESSAGE"
