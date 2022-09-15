## Changelog
### 2.0.0
- Now, if you run the executable without a specific profile, it starts reading you `credential` file and proposing the profiles that have `mfa_serial` option defined. 
- Added the possibility to use different account with MFA enaled at the same time, using a customized name you can set different `source_profile` in your `config` file.
- Removed the default value for the profile

### 1.1.1
- This version permit to use one single profile at time, running it, it generates a `temporary-credentials-with-mfa` profile in your credential file and it requires you have this temporary profile setted in all profiles in your `config` file.