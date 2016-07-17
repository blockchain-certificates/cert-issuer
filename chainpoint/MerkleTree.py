# Source: https://github.com/chainpoint/chainpoint
import json
import hashlib


# Can define and pass other hash functions here if you don't want to use SHA256
def sha256(content):
    """Finds the sha256 hash of the content."""
    content = bytes(content, 'utf-8')
    return hashlib.sha256(content).hexdigest()


def is_sha256(content):
        """Make sure this is actually an valid SHA256 hash."""
        digits58 = '0123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        for i in range(len(content)):
            if not content[i] in digits58:
                return False
        return len(content) == 64


class MerkleBranch:
    def __init__(self, left, right, hash_f=sha256):
        """Builds a Merkle branch."""
        self.left = left
        self.right = right
        self.hash_f = hash_f

    def get_parent(self):
        """Get the parent of the branch."""
        return self.hash_f(self.left + self.right)

    def contains(self, target):
        """Does the branch contain the target hash."""
        return self.left == target or self.right == target

    def get_json(self):
        """Return JSON representation of object."""
        branch = {
            "parent": self.get_parent(),
            "left": self.left,
            "right": self.right,
        }
        return branch


class MerkleTree:
    def __init__(self, hash_f=sha256):
        """Simplistic Merkle tree. Defaults to SHA256."""
        self.leaves = []
        self.hash_f = hash_f

    def add_content(self, content):
        """Hashes a content string and adds to the leaves."""
        self.leaves.append(self.hash_f(content))

    def add_hash(self, ahash):
        """Adds a single hash to the to the leaves."""
        self.leaves.append(ahash)

    def merkle_root(self):
        """Take a list of hashes, and return the merkle root hash."""
        # Generate list we can mutate
        hashes = self.leaves

        # Generate parent rows until we are left with a merkle root
        while len(hashes) > 1:
            hashes = self.merkle_pair(hashes)
        return hashes[0]

    def graph_json(self):
        hashes = self.leaves
        nodes = []
        links = []
        group = 1
        # Generate parent rows until we are left with a merkle root
        while len(hashes) > 1:
            parent_hashes = self.merkle_pair(hashes)

            for idx, value in enumerate(hashes):
                nodes.append({'id': value, 'group': group, 'parent': parent_hashes[int(idx/2)]})

            for idx, value in enumerate(parent_hashes):
                links.append({'source': value, 'target': hashes[2*idx], 'value':1})
                if len(hashes) > 2*idx+1:
                    links.append({'source': value, 'target': hashes[2*idx+1], 'value': 1})
            hashes = parent_hashes
            group += 1
        if len(hashes) == 1:
            [nodes.append({'id': n, 'group': group, 'parent': 'None'}) for n in hashes]

        graph_json = {
            'nodes': nodes,
            'links': links
        }
        return graph_json

    def merkle_pair(self, hashes, target=None):
        """
        Take a list of hashes, and return the parent row in the tree
        of merkle hashes. Optionally takes a target hash, and will only
        return part of the tree that corresponds with that hash.
        """
        # if odd then append last entry to the end of the list to make it even
        if len(hashes) % 2 == 1:
            hashes = list(hashes)
            hashes.append(hashes[-1])
        l = []

        # create an entry in the parent row for each pair in the current row
        for i in range(0, len(hashes), 2):
            l.append(self.hash_f(hashes[i] + hashes[i + 1]))
            # (optional) if the target hash is in the current row, return
            # only that pair as a MerkleBranch object
            if target == hashes[i] or target == hashes[i + 1]:
                return MerkleBranch(hashes[i], hashes[i + 1], self.hash_f)

        if target is None:
            return l  # return the parent row
        else:
            # (optional) the target hash was not found so we return
            # and empty MerkleBranch
            return MerkleBranch("", "", self.hash_f)

    def merkle_proof(self, target):
        """Gives the merkle proof of a particular leaf in the root."""

        # Generate list we can mutate
        hashes = self.leaves
        proof = MerkleProof(target, self)

        # Reduce list till we have a merkle root, but extra target
        while len(hashes) > 1:
            branch = self.merkle_pair(hashes, target)
            proof.add(branch)
            target = branch.get_parent()
            hashes = self.merkle_pair(hashes)

        return proof


class MerkleProof:
    def __init__(self, target, tree, hash_f=sha256):
        """Builds a Merkle proof."""
        self.hash_f = hash_f
        self.branches = []
        self.target = target
        self.tree = tree

    def add(self, branch):
        """Add a branch to the proof."""
        self.branches.append(branch)

    def is_valid(self):
        """Check if the target hash is in the proof."""

        # Check to see if we more than one hash
        if len(self.tree.leaves) == 1:
            return self.tree.leaves[0] == self.target

        # We assume that the leaf is contained in the
        # first branch of the proof, so then we check
        # if the parent is contained in each higher
        # branch.

        new_target = self.target
        for branch in self.branches:
            if not branch.contains(new_target):
                return False
            new_target = branch.get_parent()

        return True

    def get_json(self):
        """MerkleProof to machine readable JSON."""
        json_data = [branch.get_json() for branch in self.branches]
        return json.dumps(json_data)
