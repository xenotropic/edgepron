"""IPA -> pronunciation respelling (ported from ipa-to-pronunciation-respelling).

Ported to Python from the MIT-licensed ``ipa-to-pronunciation-respelling``
project by Attacktive (https://github.com/Attacktive/ipa-to-pronunciation-respelling).
Portions copyright 2023 Attacktive, licensed under the MIT License.
Pinned upstream commit: 69d9f60179710d98dbd4170bf02c9556449be717.
"""

from edgepron.respell.converter import ipa_to_canonical_respell

__all__ = ["ipa_to_canonical_respell"]