#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INFO_PLIST="$ROOT_DIR/ios/Runner/Info.plist"
PROJECT_FILE="$ROOT_DIR/ios/Runner.xcodeproj/project.pbxproj"
PRIVACY_FILE="$ROOT_DIR/ios/Runner/PrivacyInfo.xcprivacy"
BUNDLE_ID="${BUNDLE_ID:-ai.nuratech.nuramedical}"
IOS_DEPLOYMENT_TARGET="${IOS_DEPLOYMENT_TARGET:-15.0}"

if [[ ! -f "$INFO_PLIST" || ! -f "$PROJECT_FILE" || ! -f "$PRIVACY_FILE" ]]; then
  echo "Missing iOS project, Info.plist, or PrivacyInfo.xcprivacy" >&2
  exit 1
fi

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
text = path.read_text()
text = re.sub(r"PRODUCT_BUNDLE_IDENTIFIER = [^;]+;", f"PRODUCT_BUNDLE_IDENTIFIER = {bundle};", text)
text = re.sub(r"IPHONEOS_DEPLOYMENT_TARGET = [^;]+;", f"IPHONEOS_DEPLOYMENT_TARGET = {target};", text)
path.write_text(text)
PY

ruby - "$ROOT_DIR" <<'RUBY'
require 'xcodeproj'
root = ARGV.fetch(0)
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
echo "Prepared NURA Medical iOS release for $BUNDLE_ID (iOS $IOS_DEPLOYMENT_TARGET+)"
