---
config:
    flowchart:
        htmlLabels: true
    look: handDrawn
    layout: elk
---
graph TD
    subgraph SARIF["SARIF Input"]
        SR["SARIF Result"]
        RI["ruleId"]
        MT["message.text"]
        LV["level"]
        LO["locations[0]"]
        PR["properties"]
        URI["uri"]
        FV["fixedVersion"]
        CWE["cweId"]
        CVSS["cvssScore"]
    end

    subgraph ME["Mapping Engine"]
        FM["Field Mappings"]
        TX["Transformations"]
        MAP_SEV["map_severity<br/>none→None<br/>note→Low<br/>warning→Medium<br/>error→High"]
        CLEAN_FV["clean_fixed_version<br/>'no fix available'→''"]
        FORMAT_REM["format_remediation<br/>'X'→'Update to: X'"]
    end

    subgraph WIZ["Wiz Output"]
        VF["vulnerabilityFindings"]
        NAME["name"]
        DESC["description"]
        SEV["severity"]
        ID["id"]
        EDS["externalDetectionSource"]
        TC["targetComponent"]
        TCL["targetComponent.library"]
        FP["filePath"]
        CN["componentName"]
        TCV["fixedVersion"]
        RM["remediation<br/>(optional)"]
        OO["originalObject"]
    end

    subgraph CONST["Constants"]
        C1["'ThirdPartyAgent'"]
    end

    %% Finding Level Mappings
    RI -->|ruleId| FM
    FM -->|enabled| NAME
    RI -->|ruleId| FM
    FM -->|enabled| ID
    
    MT -->|message.text| FM
    FM -->|enabled| DESC
    
    LV -->|level| TX
    TX -->|map_severity| MAP_SEV
    MAP_SEV --> FM
    FM -->|enabled| SEV
    
    C1 -->|constant| FM
    FM -->|enabled| EDS
    
    %% Target Component Mappings
    LO -->|locations[0]| FM
    URI -->|artifactLocation.uri| FM
    FM -->|enabled| FP
    FM -->|enabled| CN
    
    PR -->|properties| FM
    FV -->|fixedVersion| TX
    TX -->|clean_fixed_version| CLEAN_FV
    CLEAN_FV --> FM
    FM -->|enabled| TCV
    
    %% Optional Fields (disabled by default)
    FV -->|properties.fixedVersion| TX
    TX -->|format_remediation| FORMAT_REM
    FORMAT_REM -.->|disabled| RM
    
    CWE -.->|disabled| FM
    CVSS -.->|disabled| FM
    
    %% Metadata
    LO -->|locations| FM
    FM -->|enabled| OO
    
    %% Output Assembly
    NAME --> VF
    DESC --> VF
    SEV --> VF
    ID --> VF
    EDS --> VF
    FP --> TCL
    CN --> TCL
    TCV --> TCL
    TCL --> TC
    TC --> VF
    OO --> VF
    RM -.-> VF

    style SARIF fill:#e1f5ff
    style ME fill:#fff3e0
    style WIZ fill:#f3e5f5
    style CONST fill:#e8f5e9
    style MAP_SEV fill:#ffe0b2
    style CLEAN_FV fill:#ffe0b2
    style FORMAT_REM fill:#ffe0b2
    style RM stroke:#999,stroke-dasharray: 5 5
    style CWE stroke:#999,stroke-dasharray: 5 5
    style CVSS stroke:#999,stroke-dasharray: 5 5
