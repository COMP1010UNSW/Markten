# Action hooks

Several hooks can be registered by Markten actions while running.

Hooks will be called in the reverse order to which they were registered.
Notably, hooks from later steps run before hooks from earlier steps.

## Teardown hooks

Teardown hooks are called after a recipe runs, and can be used to perform
clean-up. These hooks take no arguments, and should return no parameters.

## Abort hooks

Abort hooks are called if a recipe is aborted, for example due to a keyboard
interrupt. Abort hooks are only called on the action which itself failed. When
an action is aborted, all registered teardown hooks will also be run.
