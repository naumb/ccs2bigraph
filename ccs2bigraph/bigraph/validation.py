"""
Validation of bigraphs in the provided representation


"""

from dataclasses import dataclass
import logging
logger = logging.getLogger(__name__)

from .representation import *

@dataclass(frozen=True)
class BigraphValidator:
    """
    Validator Class for verifying Bigraph representations

    :param BigraphRepresentation content: The Bigraph representation to verify

    Example:
    >>> BigraphValidator(BigraphRepresentation([ControlDefinition(AtomicControl("M", 1))], [BigraphAssignment("Test", NestingBigraph(ControlBigraph(ControlByName("M"),[Link("x")]),OneBigraph()))])).validate()
    True
    """
    content: BigraphRepresentation

    def validate(self) -> bool:
        return all([
            self._validate_existing_controls(),
            self._validate_connected_ports(),
        ])
    
    def _validate_existing_controls(self) -> bool:
        def _validate_existing_controls_helper(current: Bigraph, controls: list[Control]) -> bool:
            match current:
                case OneBigraph():
                    return True
                case IdBigraph():
                    return True
                case ControlBigraph(control=control, links=_):
                    if control.name in [c.name for c in controls]: return True
                    else: return False
                case ClosedBigraph(link=_, bigraph=bigraph):
                    return _validate_existing_controls_helper(bigraph, controls)
                case NestingBigraph(control=control, inner=inner):
                    if isinstance(control, ControlBigraph) and not _validate_existing_controls_helper(control, controls): return False
                    else: return _validate_existing_controls_helper(inner, controls)
                case MergedBigraphs(merging=merging):
                    return all([_validate_existing_controls_helper(m, controls) for m in merging])
                case MergedBigraphs(merging=merging):
                    return all([_validate_existing_controls_helper(m, controls) for m in merging])
                case _:
                    raise ValueError(f"{current} is not a Bigraph.")
            return False

        controls = [c.control for c in self.content.controls]
        return all([_validate_existing_controls_helper(b.bigraph, controls) for b in self.content.bigraphs])
    
    def _validate_connected_ports(self) -> bool:
        def _validate_connected_ports_helper(current: Bigraph, controls: list[Control]) -> bool:
            match current:
                case OneBigraph():
                    return True #TODO: is this correct?
                case IdBigraph():
                    return True #TODO: is this correct?
                case ControlBigraph(control=control, links=links):
                    control_type = list(filter(lambda c: c.name == control.name, controls))[0]
                    if len(links) == control_type.arity: return True
                case ClosedBigraph(link=_, bigraph=bigraph):
                    return _validate_connected_ports_helper(bigraph, controls)
                case NestingBigraph(control=control, inner=inner):
                    if isinstance(control, ControlBigraph) and not _validate_connected_ports_helper(control, controls): return False
                    else: return _validate_connected_ports_helper(inner, controls)
                case MergedBigraphs(merging=merging):
                    return all([_validate_connected_ports_helper(m, controls) for m in merging])
                case MergedBigraphs(merging=merging):
                    return all([_validate_connected_ports_helper(m, controls) for m in merging])
                case _:
                    raise ValueError(f"{current} is not a Bigraph.")
            return False

        controls = [c.control for c in self.content.controls]
        return all([_validate_connected_ports_helper(b.bigraph, controls) for b in self.content.bigraphs])