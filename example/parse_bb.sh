docker run -i -t \
  --volume="$(pwd)/input_data:/bbx/mnt/input:ro" \
  --volume="$(pwd)/output_data:/bbx/mnt/output:rw" \
  --volume="$(pwd)/cache:/bbx/mnt/cache:rw" \
  --rm \
  williamlees/igblast \
  parse
