renew fuzzing configuration, using an engine-only stub host

in case where nodeUid has not changed, (i.e. no node visit has actually taken place) avoid writing card altogether

Consider temporarily caching card for last cardUid, avoiding need to reread/rewrite JSON

handle failure in handleCard (e.g. card present but unexpectedly invalid) by overwriting the card?

add story versioning information to stories and cards to check match

renew integration-test image rapid-build process to explore RFID speedups

# Last minute fixes

important fixes

power behaviour not yet instituted (needs to reset 'timestamp' after non-idle event, and periodically check timestamp when idle, triggering the power shutoff on D2, which should be with a resistor)

either...
* wipe rendering issue (with wipe not removing the same rectangle as was originally drawn)
* lower-right text rendering issue (with certain coordinates being incorrectly mapped to ST7920 memory)
...or...
always overwrite complete screen, never partial

* rfid can be overwritten after a failed bank read, rather than being restricted to a successful bank read which doesn't match

* add reset tags
* re-institute fuzzing with data-only cards, where main display shows just one box, and all other boxes are console-only

keep track when tag is known and outcome is known to be elsewhere - don't need to repeat all the processing

handle case where it's the same tag and nothing needs doing at all (e.g. card.nodeUid would be the same)  
keep in place saving stays up if tag pulled away - needs catching


handle case where card not read properly - don't overwrite 

