on run argv
  set movieName to item 1 of argv
  set delaySeconds to item 2 of argv
  set filePath to (path to desktop as text) & movieName
  tell application "QuickTime Player"
    activate

    close every window saving no
    set newMovieRecording to new movie recording
    repeat with i from 1 to (get video recording devices count)
      set n to (name of video recording device i as text)
      if "李先生的 iPhone (25)" is in n then
        log (get video recording device i)
        set current camera of newMovieRecording to video recording device i
        set current camera of newMovieRecording to item 1 of video recording devices
        exit repeat
      end if
    end repeat
    tell newMovieRecording
      start
      log ("start recording")
      delay delaySeconds + 1
      stop
    end tell
    export document 1 in (file filePath) using settings preset "480p"
    close document 1 saving no
  end tell
end run
