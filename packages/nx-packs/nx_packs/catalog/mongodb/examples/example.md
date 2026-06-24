# Example — MongoDB

An orders+items read-together view embeds items in the order document (no $lookup); a product catalog shared across orders is referenced by id; events are bucketed per hour to bound document growth.
