pragma solidity >=0.6.0;

contract BlockCertsOnchaining {
	enum State {not_issued, valid, revoked}

	struct Hash {
		State status;
	}

	address internal owner;
	// key: hash, value: Batch/Cert
	mapping(uint256 => Hash) public hashes;

	modifier only_owner() {
		require(
			msg.sender == owner,
			"only contract owner can issue"
		);
		_;
	}

	constructor() public {
		owner = msg.sender;
	}

	function issue_hash(uint256 _hash) public only_owner {
		hashes[_hash].status = State.valid;
	}

	function revoke_hash(uint256 _hash) public only_owner {
		hashes[_hash].status = State.revoked;
	}
}
