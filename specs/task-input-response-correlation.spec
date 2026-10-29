spec: task
name: Correlate input replies and preserve failed decisions
inherits: project
tags: [input, transport, reliability]
---

## Intent

Every steering reply or rejection settles only its originating input. Approval
and question responses retain recoverable state until the matching request or
server lifecycle confirms that the decision has settled. Local correlation
does not change the OUP wire schema.

## Acceptance Criteria

Scenario: A local rejection cannot consume an earlier steering request
  Test: input_response_local_rejection_does_not_consume_another_steer
  Given two distinct local steering requests, including identical prompt text
  When the second request is refused by the transport pending limit
  Then only its text is staged and the first request remains in flight
  And the first reply settles the first input without consuming the second

Scenario: Out of order replies retain session ownership
  Test: input_response_reordered_steers_stay_in_their_sessions
  Given steering requests from two sessions
  When the second succeeds before the first is rejected
  Then acceptance and recovery apply only to their originating sessions

Scenario: A rejected approval response can be retried
  Test: input_response_failed_approval_restores_the_original_card_and_can_retry
  Given an approval response is prepared
  When the transport refuses to send it
  Then the original card returns with its identity preserved
  And a later successful response clears its backup

Scenario: A rejected question preserves the selected answer
  Test: input_response_failed_question_preserves_answers
  Given a question with an answer selected
  When its response is rejected
  Then the original picker and answer are restored
  And a successful retry clears the retained state

Scenario: A decided approval cannot be resurrected by a late failure
  Test: input_response_late_approval_error_does_not_resurrect_a_decided_card
  Given an approval response is in flight
  When a decided notification precedes a late transport failure
  Then the card remains settled

Scenario: A failed peer approval remains owned by its background session
  Test: input_response_peer_approval_failure_stays_in_background
  Given a peer approval is answered without selecting that peer
  When the response is rejected
  Then its original card returns only to that peer's pending stash

Scenario: Disconnect cancellation recovers each input exactly once
  Test: input_response_disconnect_cancels_only_the_matching_inputs
  Given multiple steering requests are in flight
  When the transport cancels them on disconnect
  Then each originating input is staged once
