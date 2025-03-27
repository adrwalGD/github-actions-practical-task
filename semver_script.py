import sys
import semver

current_ver = sys.argv[1]
bump_type = sys.argv[2]

if bump_type == "major":
    new_ver = semver.bump_major(current_ver)
elif bump_type == "minor":
    new_ver = semver.bump_minor(current_ver)
elif bump_type == "patch":
    new_ver = semver.bump_patch(current_ver)
else:
    print("Invalid bump type")
    sys.exit(1)

print(new_ver)
