import argparse
import os


class Arguments:
    """
    Validate the arguments and check that they meet the basic requirements
    for running the simulation
    """
    def __init__(self, selected_map: str = "",
                 visual_representation: str = "") -> None:
        # Get Arguments from command line
        new_args = argparse.ArgumentParser()

        new_args.add_argument(
            "--map",
            dest="selected_map",
            type=str,
            default=""
        )

        new_args.add_argument(
            "--representation",
            dest="visual_representation",
            type=str,
            choices=["terminal", "graphical", "both"],
            default="both"
        )

        args = new_args.parse_args()

        # If the class received arguments from the class creation,
        # those arguments are preferred
        if not selected_map:
            self.selected_map = args.selected_map
        else:
            self.selected_map = selected_map

        if not visual_representation:
            self.visual_representation = args.visual_representation
        else:
            self.visual_representation = visual_representation

        # Validate arguments
        self.validate_arguments()

    def validate_arguments(self) -> None:
        if not os.access(self.selected_map, os.R_OK):
            raise ValueError("Cannot read from the selected map: "
                             f"'{self.selected_map}'")
        if self.visual_representation not in ["terminal", "graphical", "both"]:
            raise ValueError("Invalid representation option: "
                             f"'{self.visual_representation}'")
