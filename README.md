# Taint Bomb auto Java Obfuscator by 조준발싸!

---


<div style="text-align: center;"><img src="./.idea/icon.png" width="600px" height="600px" alt="Taint Bomb logo"></div>


####
<div style="text-align: center">
  <a href="https://github.com/JoJoonBalSsa/Taint-Bomb/releases"><img src="https://img.shields.io/github/release/JoJoonBalSsa/Taint-Bomb.svg" width="100px"></a>
  <img alt="JetBrains Plugin Downloads" src="https://img.shields.io/jetbrains/plugin/d/25629" width="100px">
  <img alt="JetBrains Plugin Rating" src="https://img.shields.io/jetbrains/plugin/r/rating/25629" width="90px">
</div>

<div style="text-align: center">
  <a href="https://plugins.jetbrains.com/plugin/25629-taint-bomb-auto-java-obfuscator">
    <div><img alt="Get from marketplace" src="./docs/getFromMarketplace.png" width="500px"></div>
  </a>
</div>

<!-- Plugin description -->
  Taint Bomb is a one click auto Java obfuscator IntelliJ plugin, with light but strong obfuscate feature. It analysis project's source codes with Taint Analysis and set obfuscate level by defined sensitivity.
  If you want to report a bug or request a feature, please feel free to leave an [issue](https://github.com/JoJoonBalSsa/Taint-Bomb/issues).

  ---

  Taint Bomb은 IntelliJ에서 작동하는 원클릭 자동 자바 난독화 플러그인입니다. 가볍지만 강력한 난독화 기능을 지원하며, Taint 분석을 통해 코드의 민감도를 식별하고 그 결과에 기반한 차등적 난독화를 수행합니다.
  버그나 기능 추가를 원하신다면 [이슈](https://github.com/JoJoonBalSsa/Taint-Bomb/issues)를 남겨주세요.
<!-- Plugin description end -->




<div style="text-align: center">
  <a href="./docs/README-eng.md">
    <div style="font-size:400%">🇺🇸 English Docs</div>
  </a>
</div>

# 요구사항

---

## 플러그인 요구사항
- 인터넷 연결
  - 파이썬 라이브러리를 설치하는데 필요합니다.
- python 3.7 이상
- IntelliJ : 2023.3 이상 / Android Studio Iguana 이상
- Windows, macOS, Linux 지원

## 난독화 대상 프로젝트 요구사항
- Java SE 8 문법 지원
  - 다음 문서에 해당하는 문법을 가져야 합니다. http://docs.oracle.com/javase/specs/jls/se8/html/
- gradle 8이나 9 또는 maven 3.9 이상
  - gradle 사용시 build.gradle에 jar 속성이 정의되어 있어야 합니다.
- 사용법 - 주의사항 참고

# 사용법

---

1. 플러그인을 IntelliJ에 설치합니다.
  - [GitHub Releases](https://github.com/JoJoonBalSsa/Taint-Bomb/releases)를 확인하거나 [IntelliJ marketplace](https://plugins.jetbrains.com/plugin/25629-taint-bomb-auto-java-obfuscator)에서 설치합니다. 
2. 난독화 할 프로젝트를 IntelliJ에서 열고, Taint Bomb 아이콘을 찾아 창을 엽니다. 
3. Configuration에서 적용할 난독화 기법, AI api 키(선택 사항)을 설정해줍니다. 
4. Obfuscate 버튼을 클릭합니다. 
5. 프로젝트 폴더 내에 난독화 된 프로젝트 폴더인 'obfuscated_project_folder' 가 생성되며, 폴더 내부에는 소스코드 분석 결과(taint_analysis.txt & anlysis_result.md)와 LLM을 이용한 취약점 분석 결과가 생성됩니다.

## [주의 사항]
- 난독화 전 프로젝트의 모든 override함수에 @Override 어노테이션이 붙어있어야 합니다.
- 테스트 코드가 포함된 프로젝트는 난독화나 빌드가 제대로 이루어지지 않을 수 있습니다.
- Taint 분석 결과 민감도 2 단계와 3 단계 흐름이 존재하지 않는다면 해당 난독화는 수행되지 않습니다. (연산자 난독화, 함수 분할, 더미 코드 삽입)
