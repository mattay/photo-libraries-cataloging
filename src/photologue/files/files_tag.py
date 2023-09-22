import os.path
# import logging

# https://github.com/RhetTbull/osxmetadata
from osxmetadata import (
    OSXMetaData,
    Tag,
    # FINDER_COLOR_NONE,
    FINDER_COLOR_GRAY,
    # FINDER_COLOR_GREEN,
    # FINDER_COLOR_PURPLE,
    FINDER_COLOR_BLUE,
    FINDER_COLOR_YELLOW,
    FINDER_COLOR_RED,
    FINDER_COLOR_ORANGE,
)

VALID_STATES = {
    'master': Tag("00 Master", FINDER_COLOR_BLUE),
    'copy': Tag("01 Copy", FINDER_COLOR_GRAY),
    'ignored': Tag("02 Ignored", FINDER_COLOR_YELLOW),
    'filtered': Tag("03 Filtered", FINDER_COLOR_ORANGE),
    'unresolved': Tag("04 Unresolved", FINDER_COLOR_RED),
    'oops': Tag("05 Oops", FINDER_COLOR_RED),
}


# Update tag on a file
def update_tag(file_path: str, state: str) -> None:
    if not os.path.isfile(file_path):
        print(f'File not found {file_path}')
        return

    if state not in VALID_STATES.keys():
        print(f'Invalid tag "{state}"')
        return

    new_tags: list = []
    existing_tags: list = []
    try:
        md = OSXMetaData(file_path)
        existing_tags = md.get("tags")

        for tag in existing_tags:
            if tag in VALID_STATES.values():
                # Can only have one state at time
                continue
            new_tags.append(tag)

        # Add updated state
        new_tags.append(VALID_STATES[state])
        md.set('tags', new_tags)

    except OSError as e:
        print(f"Error adding tag {state} to {file_path}: {e}")
