# Game Frontend Media Auditor

Meant to replace the Audit feature in Launchbox because it's too slow and bulky. I just wanted something simple.

![image](https://github.com/dsync89/game-frontend-media-auditor/assets/12208390/2986204a-89fc-4db8-8c3c-d86b0ec40a6b)

Launchbox Audit window -> too slow and didn't have image preview.
![image](https://github.com/dsync89/game-frontend-media-auditor/assets/12208390/d85214fb-491b-4814-aad0-a4c1ca44fbff)

# How It Works

The image matching is done based on 

So if the ROM is 'Addams Family (2003).ahk', it will regex it to 'Addams Family'. Then it will find all images in clear logo and playfield folder and do the same regex on all pictures there. It then compare the regexed string of the rom and the image. 

The regex is done by extracting from the first character (alphanumeric) till the first left bracket `(` or the first left square bracket `[` it find due to the way the tables are name and not standardize. It's more accurate to match without those brackets because the table name rarely changes. Launchbox treat () and [] as version, so it will match with the same logic.

# TODO
- Resize frame elements
- Coloring
