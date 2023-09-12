rule XYLENT_TEST_WORD {
   meta:
      description = "Detection of word file designed as a harmless test sample for Xylent Antimalware"
      author = "Rutuj Runwal"
      reference = "TODO_ADD_GITHUB_REFERENCE"
      score = 90
   strings:
      $header = { D0 CF 11 E0 A1 B1 1A E1 }
      $s1 = "Rutuj"
      $s2 = "Runwal"
      $s3 = "Xylent"
   condition:
      $header at 0 and all of ($s*)
}
