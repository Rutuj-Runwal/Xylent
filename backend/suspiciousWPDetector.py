import re
import math

class SuspiciousWPDetector:
    def split_in_chunks(self,text, chunk_size):
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i + chunk_size])
        if len(chunks) > 1 and len(chunks[-1]) < 10:
            chunks[-2] += chunks[-1]
            chunks.pop(-1)
        return chunks


    def unique_chars_per_chunk_percentage(self,text, chunk_size):
        chunks = self.split_in_chunks(text, chunk_size)
        unique_chars_percentages = []
        for chunk in chunks:
            total = len(chunk)
            unique = len(set(chunk))
            unique_chars_percentages.append(unique / total)
        return sum(unique_chars_percentages) / len(unique_chars_percentages) * 100


    def vowels_percentage(self,text):
        vowels = 0
        total = 0
        for c in text:
            if not c.isalpha():
                continue
            total += 1
            if c in "aeiouAEIOU":
                vowels += 1
        if total != 0:
            return vowels / total * 100
        else:
            return 0


    def word_to_char_ratio(self,text):
        chars = len(text)
        words = len([x for x in re.split(r"[\W_]", text) if x.strip() != ""])
        return words / chars * 100


    def deviation_score(self,percentage, lower_bound, upper_bound):
        if percentage < lower_bound:
            return math.log(lower_bound - percentage, lower_bound) * 100
        elif percentage > upper_bound:
            return math.log(percentage - upper_bound, 100 - upper_bound) * 100
        else:
            return 0


    def classify(self,text):
        if text is None or len(text) == 0:
            return 0.0
        ucpcp = self.unique_chars_per_chunk_percentage(text, 10)
        vp = self.vowels_percentage(text)
        wtcr = self.word_to_char_ratio(text)

        ucpcp_dev = max(self.deviation_score(ucpcp, 45, 50), 1)
        vp_dev = max(self.deviation_score(vp, 35, 45), 1)
        wtcr_dev = max(self.deviation_score(wtcr, 15, 20), 1)

        score = math.floor(max((math.log10(ucpcp_dev) + math.log10(vp_dev) +
                    math.log10(wtcr_dev)) / 6 * 100, 1))
        if score>=75 and score<80:
            return "Unknown"
        elif score>=80 and score<90:
            return "Suspicious"
        elif score>=90:
            return "Malware"
        else:
            return "Safe"