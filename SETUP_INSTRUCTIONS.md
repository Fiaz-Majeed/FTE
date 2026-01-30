# Setting LinkedIn Environment Variables

## On Windows:
```cmd
set LINKEDIN_USERNAME=fiaz.majeed@uog.edu.pk
set LINKEDIN_PASSWORD=1DR2IT3UOG
```

## On Unix/Linux/Mac:
```bash
export LINKEDIN_USERNAME=fiaz.majeed@uog.edu.pk
export LINKEDIN_PASSWORD=1DR2IT3UOG
```

## Permanently Setting Environment Variables (Windows):
1. Press Win+R, type "sysdm.cpl", press Enter
2. Click "Advanced" tab
3. Click "Environment Variables"
4. Under "User variables", click "New"
5. Variable name: `LINKEDIN_USERNAME`, Variable value: `fiaz.majeed@uog.edu.pk`
6. Repeat for password: Variable name: `LINKEDIN_PASSWORD`, Variable value: `1DR2IT3UOG`

## Permanently Setting Environment Variables (Unix/Linux/Mac):
Add these lines to your ~/.bashrc, ~/.zshrc, or ~/.profile:
```bash
export LINKEDIN_USERNAME=fiaz.majeed@uog.edu.pk
export LINKEDIN_PASSWORD=1DR2IT3UOG
```
Then run: `source ~/.bashrc` (or the appropriate file)

## Alternative: Update config.json
You can also add your credentials directly to the config.json file in the root directory.