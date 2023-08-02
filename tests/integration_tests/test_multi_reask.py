import openai

import guardrails as gd
from tests.integration_tests.mock_llm_outputs import openai_completion_create
from tests.integration_tests.test_assets import python_rail


def test_multi_reask(mocker):
    """Test that parallel reasking works."""
    mocker.patch(
        "guardrails.llm_providers.openai_wrapper", new=openai_completion_create
    )

    guard = gd.Guard.from_rail_string(python_rail.RAIL_SPEC_WITH_VALIDATOR_PARALLELISM)

    _, final_output = guard(
        llm_api=openai.Completion.create,
        engine="text-davinci-003",
        num_reasks=5,
    )

    # Assertions are made on the guard state object.
    # assert final_output == python_rail

    guard_history = guard.guard_state.most_recent_call.history

    assert len(guard_history) == 3

    assert guard_history[0].prompt.source == python_rail.VALIDATOR_PARALLELISM_PROMPT_1
    assert guard_history[0].output == python_rail.VALIDATOR_PARALLELISM_RESPONSE_1
    assert (
        guard_history[0].validated_output == python_rail.VALIDATOR_PARALLELISM_REASK_1
    )

    assert guard_history[1].prompt.source == python_rail.VALIDATOR_PARALLELISM_PROMPT_2
    assert guard_history[1].output == python_rail.VALIDATOR_PARALLELISM_RESPONSE_2
    assert (
        guard_history[1].validated_output == python_rail.VALIDATOR_PARALLELISM_REASK_2
    )

    assert guard_history[2].prompt.source == python_rail.VALIDATOR_PARALLELISM_PROMPT_3
    assert guard_history[2].output == python_rail.VALIDATOR_PARALLELISM_RESPONSE_3
    assert (
        guard_history[2].validated_output
        == python_rail.VALIDATOR_PARALLELISM_RESPONSE_3
    )