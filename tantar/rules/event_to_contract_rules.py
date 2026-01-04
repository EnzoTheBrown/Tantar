from typing import Optional, List
from schemas.vector import ContractChunk
from schemas.objects import Event


async def find_matching_contract_chunks(
    account_id: str,
    siren: str,
    event: Event,
) -> Optional[List[ContractChunk]]:
    return None
