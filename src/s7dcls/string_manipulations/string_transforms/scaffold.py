from collections.abc import Sequence
from dataclasses import dataclass

from s7dcls.string_manipulations.string_transforms.protocol import StringTransformProtocol


@dataclass(kw_only=True, frozen=True)
class SequenceTransform(StringTransformProtocol):
    transforms: Sequence[StringTransformProtocol] = ()

    def __call__(self, string):
        for transform in self.transforms:
            string = transform(string)

        return string
