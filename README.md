# TransPerthTrainViewer
Trying to create a web-based visual representation of the "live" train data provided by TransPerth. A public API would've made this much easier.

## Notes
- Fetching script takes about 30 minutes to complete to prevent 403s.
- That's fine because it contains like 2 hours of train data. Haven't actually tested it back to back though...

## Todo

- redesign the SVG to be more detailed.
- work out how to fix trains finishing early because the final station isn't in the list of stops.
- get trains to follow the SVG correctly.
- Setup github action to automate the data updates
