import argparse
from pydantic import BaseModel, model_validator, Field


class Parser(BaseModel):
    selected_map: str = Field(default="")
    visual_representation: str = Field(default="both")

    @model_validator(mode="after")
    def validate_arguments(self) -> "Parser":
        return self

    def get_map(self) -> str:
        return self.selected_map

    def get_representation(self) -> str:
        return self.visual_representation

    @classmethod
    def get_args(cls) -> "Parser":
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
            default=""
        )

        args = new_args.parse_args()

        return cls(**vars(args))
