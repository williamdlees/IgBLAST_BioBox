docker run -i -t ^
  --volume="%cd%\input_data:/bbx/mnt/input:ro" ^
  --volume="%cd%\output_data:/bbx/mnt/output:rw" ^
  --volume="%cd%\cache:/bbx/mnt/cache:rw" ^
  --rm ^
  williamlees/igblast ^
  parse
