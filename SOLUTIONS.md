# Issue: Base64 image decoding error

## Problem Description

- What was the unexpected behavior?
when attempting to save an artwork with a base64-encoded image, the app returned an error saying "Error decoding base64 image data".

- What should have happened instead?
The app should have successfully decoded the base64 image string and stored the image as binary data in the database.

- How was this issue discovered?
The issue was discovered when testing the saving artwork feature on the website.

## Root Cause Analysis

- What was the underlying cause?
The image data passed to the app was missing necessary padding (= characters), which is required for base64 encoding to function correctly

- What assumptions were incorrect?
It was assumed that the base64 data would always have the correct padding or that it was automatically handled.

- What dependencies were involved?
The issue was related to the standard Python base64 library, which was used to decode the base64 image string.


## Resolution

- How was it fixed? (or planned fix if unresolved)
The issue was fixed by adding a padding check and correcting the base64 data before attempting to decode it

- What changes were made?
The decode_base64 function was updated to add padding if the base64 string's length was not a multiple of 4

- What alternatives were considered?
An alternative approach considered was to use a third-party library like Pillow to handle the image data.

## Prevention

- How can similar issues be prevented?
Use a helper function to validate base64 strings, especially with paddings.

- What lessons were learned?
 Ensure all input data formats (especially base64) are validated before use

- What warning signs should be watched for?
 If base64 decoding fails, check the length of the string and verify it is correctly padded