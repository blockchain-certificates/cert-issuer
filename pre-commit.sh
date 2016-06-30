#!/bin/sh

echo "running pre-commit hook..."

# run tests with staged changes. Fail if tests fail
git stash -q --keep-index
./run_tests.sh
RESULT=$?
git stash pop -q
[ $RESULT -ne 0 ] && exit 1

# slurp in docker / quick start steps, which are reused in README.md and docs
echo "copying docker instructions to docs/ dir"
docker=`awk '/\start_docker_instructions"/{f=1;next}/\end_docker_instructions/{f=0}f' README.md`
echo "$docker" | tee docs/docker.md >> /dev/null
echo "finished running pre-commit hook"

exit 0