import app
from app import App, Apt, ConfigModification, AptRepo
from common import OS

current_os = OS.ubuntu

# noinspection LongLine
# @formatter:off
apps = [
    # App(
    #     ({
    #         OS.ubuntu: Apt(PackageName="firefox", RepoOrPpa=AptPpa("ppa:mozillateam/ppa")),
    #         OS.fedora: Dnf(PackageName="firefox")
    #     })[current_os]
    # ),
    # App(Installation=Apt(PackageName="vlc")),
    # App(Snap("multipass")),
    # App("neofetch"),
    App(
        Installation=Apt(
            "codium",
            AptRepo(
                KeyUrl="https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/raw/master/pub.gpg",
                RepoSourceStr="deb https://download.vscodium.com/debs vscodium main"
            )
        ),
        Settings=[
            ConfigModification(
                Path="/usr/share/codium/resources/app/product.json",
                ModifyAction=lambda cfg: cfg.modify_chained(
                    [
                        lambda c: c["extensionEnabledApiProposals"]["GitHub.copilot"].set(["inlineCompletionsAdditions"]),
                        lambda c: c["extensionEnabledApiProposals"]["GitHub.copilot-nightly"].set(["inlineCompletionsAdditions"]),
                        lambda c: c["extensionEnabledApiProposals"]["GitHub.copilot-chat"].set(["handleIssueUri", "interactive", "terminalDataWriteEvent", "terminalExecuteCommandEvent", "terminalSelection", "terminalQuickFixProvider", "chatParticipant", "chatParticipantAdditions", "defaultChatParticipant", "chatVariableResolver", "chatProvider", "mappedEditsProvider", "aiRelatedInformation", "codeActionAI", "findTextInFiles", "textSearchProvider", "contribSourceControlInputBoxMenu", "newSymbolNamesProvider", "findFiles2"]),
                        lambda c: c["extensionVirtualWorkspacesSupport"]["trustedExtensionAuthAccess"].set(["vscode.git", "vscode.github", "github.remotehub", "github.vscode-pull-request-github", "github.codespaces", "github.copilot", "github.copilot-chat"]),
                        lambda c: c["extensionVirtualWorkspacesSupport"]["trustedExtensionProtocolHandlers"].set(["vscode.git", "vscode.github-authentication"])
                    ]
                )
            )
        ]
    )
]
# @formatter:on

app.handle(apps)

# modify_file.modify_structured_config(
#     path="/file1.json",
#     modify_action=lambda cfg: cfg["cars"]["car9"].set("Mercedes"),
# )
#
# modify_file.modify_structured_config(
#     path="/file2.json",
#     modify_action=lambda lst: lst.append("Mercedes"),
# )
#
# modify_file.modify_structured_config(
#     path="/file3.json",
#     modify_action=lambda dct: dct.modify_chained(
#         [
#             lambda x: x.set({"friends": ["Alice", "Bob"]}),
#             lambda x: x["age"].set(25),
#             lambda x: x["names"].set(["Alice", "Bob"]),
#             lambda x: x["names"].append("Charlie"),
#         ]
#     )
# )
