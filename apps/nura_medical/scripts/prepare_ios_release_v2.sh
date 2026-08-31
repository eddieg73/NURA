#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export NURA_MEDICAL_ROOT="$ROOT_DIR"
INFO_PLIST="$ROOT_DIR/ios/Runner/Info.plist"
PROJECT_FILE="$ROOT_DIR/ios/Runner.xcodeproj/project.pbxproj"
PRIVACY_FILE="$ROOT_DIR/ios/Runner/PrivacyInfo.xcprivacy"
BUNDLE_ID="${BUNDLE_ID:-ai.nuratech.nuramedical}"
IOS_DEPLOYMENT_TARGET="${IOS_DEPLOYMENT_TARGET:-15.0}"

for required in "$INFO_PLIST" "$PROJECT_FILE" "$PRIVACY_FILE"; do
  if [[ ! -f "$required" ]]; then
    echo "Required iOS release file is missing: $required" >&2
    exit 1
  fi
done

set_plist_string() {
  local key="$1"
  local value="$2"
  /usr/libexec/PlistBuddy -c "Set :$key $value" "$INFO_PLIST" 2>/dev/null || \
    /usr/libexec/PlistBuddy -c "Add :$key string $value" "$INFO_PLIST"
}

set_plist_bool() {
  local key="$1"
  local value="$2"
  /usr/libexec/PlistBuddy -c "Set :$key $value" "$INFO_PLIST" 2>/dev/null || \
    /usr/libexec/PlistBuddy -c "Add :$key bool $value" "$INFO_PLIST"
}

set_plist_string "CFBundleDisplayName" "NURA Medical"
set_plist_string "NSMicrophoneUsageDescription" \
  "NURA uses the microphone only when a clinician starts dictation to create a provider-review draft."
set_plist_string "NSSpeechRecognitionUsageDescription" \
  "NURA converts clinician-initiated dictation into editable text for a provider-review draft."
set_plist_bool "ITSAppUsesNonExemptEncryption" "false"
set_plist_bool "UIFileSharingEnabled" "false"
set_plist_bool "LSSupportsOpeningDocumentsInPlace" "false"

python3 - "$PROJECT_FILE" "$BUNDLE_ID" "$IOS_DEPLOYMENT_TARGET" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
bundle = sys.argv[2]
target = sys.argv[3]
text = path.read_text(encoding="utf-8")
text, bundle_count = re.subn(
    r"PRODUCT_BUNDLE_IDENTIFIER = [^;]+;",
    f"PRODUCT_BUNDLE_IDENTIFIER = {bundle};",
    text,
)
text, target_count = re.subn(
    r"IPHONEOS_DEPLOYMENT_TARGET = [^;]+;",
    f"IPHONEOS_DEPLOYMENT_TARGET = {target};",
    text,
)
if bundle_count == 0:
    raise SystemExit("No PRODUCT_BUNDLE_IDENTIFIER setting was found")
if target_count == 0:
    raise SystemExit("No IPHONEOS_DEPLOYMENT_TARGET setting was found")
path.write_text(text, encoding="utf-8")
PY

ruby <<'RUBY'
require 'xcodeproj'
root = ENV.fetch('NURA_MEDICAL_ROOT')
project_path = File.join(root, 'ios', 'Runner.xcodeproj')
privacy_path = File.join(root, 'ios', 'Runner', 'PrivacyInfo.xcprivacy')
project = Xcodeproj::Project.open(project_path)
target = project.targets.find { |item| item.name == 'Runner' }
abort('Runner target not found') unless target
runner_group = project.main_group.find_subpath('Runner', true)
file = runner_group.files.find { |item| item.path == 'PrivacyInfo.xcprivacy' }
file ||= runner_group.new_file(privacy_path)
unless target.resources_build_phase.files_references.include?(file)
  target.resources_build_phase.add_file_reference(file, true)
end
project.save
RUBY

plutil -lint "$INFO_PLIST"
plutil -lint "$PRIVACY_FILE"
grep -q "PRODUCT_BUNDLE_IDENTIFIER = $BUNDLE_ID;" "$PROJECT_FILE"
grep -q "IPHONEOS_DEPLOYMENT_TARGET = $IOS_DEPLOYMENT_TARGET;" "$PROJECT_FILE"

echo "Prepared NURA Medical iOS release for $BUNDLE_ID (iOS $IOS_DEPLOYMENT_TARGET+)"
