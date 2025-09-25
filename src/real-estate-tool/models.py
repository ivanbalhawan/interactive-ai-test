from __future__ import annotations

from typing import Literal, TypedDict

from pydantic import BaseModel, Field


# TODO: City and neighborhood should be titled
class LocationDetails(BaseModel):
    city: str
    neighborhood: str


class PropertyFeatures(BaseModel):
    bedrooms: int | None = None
    bathrooms: int | None = None
    area_sqm: int | None = None
    balcony: bool | None = None
    parking: bool | None = None
    elevator: bool | None = None
    floor: int | None = None
    year_built: int | None = None


class UserInput(BaseModel):
    title: str  # This field is required as there are no other fields that determine if the listing is an apartment or a house  # noqa F401
    location_details: LocationDetails
    property_features: PropertyFeatures
    price: int
    listing_type: Literal["sale", "rent"]
    language: Literal["en", "pt"] = "en"

    @classmethod
    def from_dict(cls, user_input_dict: dict) -> UserInput:
        location_details = LocationDetails(**user_input_dict.pop("location"))
        property_features = PropertyFeatures(**user_input_dict.pop("features"))
        user_input_dict.update(
            {
                "location_details": location_details,
                "property_features": property_features,
            }
        )
        return cls(**user_input_dict)

    @property
    def key_features_list(self) -> list[str]:
        key_features_list = list()
        if area_sqm := self.property_features.area_sqm:
            key_features_list.append(f"{area_sqm} sqm of living space")
        bedrooms = self.property_features.bedrooms
        bathrooms = self.property_features.bathrooms
        if bedrooms:
            bed_label = "bedroom" if bedrooms == 1 else "bedrooms"
            if bathrooms:
                bath_label = "bathroom" if bathrooms == 1 else "bathrooms"
                key_features_list.append(f"{bedrooms} {bed_label} and {bathrooms} {bath_label}")
            else:
                key_features_list.append(f"{bedrooms} {bed_label}")
        if self.property_features.balcony:
            key_features_list.append("Private balcony")
        if self.property_features.elevator:
            key_features_list.append("Elevator access")
        if self.property_features.parking:
            key_features_list.append("Dedicated parking")
        key_features_list.append(f"Located in {self.location_details.neighborhood.title()}, {self.location_details.city.title()}")

        return key_features_list


    def build_features_paragraph(self) -> str:
        property_features = self.property_features
        title = self.title
        str_description = f"{title}\n"

        if bedrooms := property_features.bedrooms:
            str_description += f"Number of bedrooms: {bedrooms}.\n"
        if bathrooms := property_features.bathrooms:
            str_description += f"Number of bathrooms: {bathrooms}.\n"
        if area_sqm := property_features.area_sqm:
            str_description += (
                f"The property has {area_sqm} square meters of living space.\n"
            )
        if property_features.balcony:
            str_description += "The property has a balcony.\n"
        if property_features.parking:
            str_description += "The property has a parking space.\n"
        if property_features.elevator:
            str_description += "The property has an elevator.\n"
        if floor := property_features.floor:
            str_description += f"The property is located on the {floor} floor.\n"
        if year_built := property_features.year_built:
            str_description += f"The property was built in {year_built}.\n"

        str_description += f"The property is available for {self.listing_type}"
        if price := self.price:
            str_description += f"at EUR {price}.\n"
        else:
            str_description += ".\n"

        location_details = self.location_details
        str_description += f"The property is located in the {location_details.neighborhood} neighborhood of {location_details.city}.\n"

        return str_description


class PropertyAdjectives(BaseModel):
    area_size: list[str] = Field(
        ...,
        description="List of adjectives/phrases relating to the size of the property and whether or not it features a balcony.",
    )
    year_built: list[str] = Field(
        ...,
        description="List of adjectives/phrases relating to the age of the property",
    )
    ideal_occupants: list[str] = Field(
        ...,
        description="List of phrases relating to the ideal occupants, e.g. 'ideal for couples'",
    )
    amenities: list[str] = Field(
        ...,
        description="List of phrases/adjectives relating to the available amenities, if any.",
    )

    @property
    def all_adjectives_list(self) -> list[str]:
        return self.area_size + self.year_built + self.ideal_occupants + self.amenities


class State(TypedDict):
    user_input: UserInput
    title: str
    meta_description: str
    headline: str
    full_description: str
    key_features_list: list[str]
    neighborhood_summary: str
    call_to_action: str
    adjectives: PropertyAdjectives


class OutputState(BaseModel):
    title: str
    meta_description: str
    headline: str
    full_description: str
    key_features_list: list[str]
    neighborhood_summary: str
    call_to_action: str

    def to_html(self) -> str:
        key_features_html = (
            "<ul id=\"key-features\">\n  "
            + "\n  ".join([f"<li>{feature}</li>" for feature in self.key_features_list])
            + "\n</ul>"
        )
        html_str = (
            ""
            + f"<title>{self.title}</title>\n"
            + f"<meta name=\"description\" content=\"{self.meta_description}\"\n"
            + f"<h1>{self.headline}</h1>\n"
            + f"<section_id=\"description\">\n  <p>\n{self.full_description}\n  </p>\n</section>\n"
            + key_features_html
            + f"<section id=\"neighborhood\">\n  <p>\n  {self.neighborhood_summary}\n  </p>\n</section>\n"
            + f"<p class=\"call-to-action\">{self.call_to_action}</p>"
        )
        return html_str


    def to_str(self) -> str:
        output_str = ""
        for field in self.model_fields_set:
            output_str += f"**{field}**: {getattr(self, field)}\n\n"
        return output_str
