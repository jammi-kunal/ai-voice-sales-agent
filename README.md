# Dee — AI Voice Sales Agent

An AI-powered voice sales agent built with Rasa and Python that can conduct natural-language sales conversations with prospects, understand their intent, handle common objections, answer questions, and guide interested prospects toward scheduling a meeting.

## Overview

Dee is designed as an automated sales representative that can handle an outbound sales conversation from the initial greeting through lead qualification and meeting scheduling.

The system combines conversational AI with speech technologies to create a voice-based interaction:

Audio → Speech-to-Text → Rasa NLU & Dialogue Management → Text-to-Speech → Audio Response

The project also integrates external services for email follow-ups and Google Calendar/Google Meet scheduling.

## Key Features

- Voice-based conversational sales agent
- Natural-language intent recognition using Rasa
- Entity extraction for prospect and meeting information
- Context-aware conversational flows
- Handling of common sales objections and negative responses
- Product/technology/pricing FAQ handling
- Demo and information requests
- Detection of whether the prospect is the correct contact
- Lead redirection and email follow-up
- Meeting date/time collection and confirmation
- Google Calendar and Google Meet integration
- Speech-to-Text using OpenAI Whisper
- Text-to-Speech using external voice providers
- REST APIs built with FastAPI
- Docker-based deployment

## Conversational Flow

The agent is designed around a typical outbound sales conversation:

1. **Greet the prospect**
2. **Introduce the product/service**
3. **Determine whether the prospect is interested**
4. **Answer questions and FAQs**
5. **Handle objections or negative responses**
6. **Determine whether the person is the appropriate contact**
7. **Redirect to the appropriate person when necessary**
8. **Offer additional information or a demo**
9. **Collect meeting availability**
10. **Confirm the meeting details**
11. **Schedule a follow-up meeting**

The conversation uses Rasa intents, entities, slots, forms, rules, stories, and custom actions to maintain state throughout the interaction.

## Architecture

```text
                    ┌──────────────────┐
                    │   User / Prospect│
                    └────────┬─────────┘
                             │
                         Voice Input
                             │
                             ▼
                    ┌──────────────────┐
                    │   FastAPI Voice  │
                    │     Service      │
                    └────────┬─────────┘
                             │
                        Whisper STT
                             │
                             ▼
                    ┌──────────────────┐
                    │   Rasa NLU &     │
                    │ Dialogue Engine  │
                    └────────┬─────────┘
                             │
                  ┌──────────┴──────────┐
                  │                     │
                  ▼                     ▼
          Custom Actions          Conversation
          & Integrations             Response
                  │
       ┌──────────┼───────────┐
       │          │           │
       ▼          ▼           ▼
     Email    Google Calendar  Other APIs
                   │
                   ▼
              Google Meet
                             │
                             ▼
                    ┌──────────────────┐
                    │   Text-to-Speech │
                    └────────┬─────────┘
                             │
                             ▼
                       Voice Response
