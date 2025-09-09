import * as vscode from 'vscode';
import { WorkflowManager, WorkflowStatus } from './workflowManager';

export class ZSCEAgentProvider implements vscode.TreeDataProvider<vscode.TreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<vscode.TreeItem | undefined | null | void> = new vscode.EventEmitter<vscode.TreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<vscode.TreeItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(private workflowManager: WorkflowManager) {
        // 监听工作流状态变化
        setInterval(() => {
            this._onDidChangeTreeData.fire();
        }, 1000);
    }

    getTreeItem(element: vscode.TreeItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: vscode.TreeItem): Thenable<vscode.TreeItem[]> {
        if (!element) {
            return this.getRootItems();
        }
        return Promise.resolve([]);
    }

    private async getRootItems(): Promise<vscode.TreeItem[]> {
        const items: vscode.TreeItem[] = [];

        // 添加工作流状态
        const currentWorkflow = this.workflowManager.getCurrentWorkflow();
        if (currentWorkflow) {
            const workflowItem = new vscode.TreeItem(
                `Workflow: ${currentWorkflow.status}`,
                vscode.TreeItemCollapsibleState.None
            );
            workflowItem.description = currentWorkflow.currentStep;
            workflowItem.iconPath = this.getStatusIcon(currentWorkflow.status);
            workflowItem.tooltip = `Progress: ${currentWorkflow.progress}%`;
            items.push(workflowItem);
        }

        // 添加快速操作
        const startWorkflowItem = new vscode.TreeItem(
            'Start New Workflow',
            vscode.TreeItemCollapsibleState.None
        );
        startWorkflowItem.iconPath = new vscode.ThemeIcon('play');
        startWorkflowItem.command = {
            command: 'zswe-agent.startWorkflow',
            title: 'Start New Workflow'
        };
        items.push(startWorkflowItem);

        // 添加配置项
        const configItem = new vscode.TreeItem(
            'Configuration',
            vscode.TreeItemCollapsibleState.Collapsed
        );
        configItem.iconPath = new vscode.ThemeIcon('gear');
        items.push(configItem);

        return items;
    }

    private getStatusIcon(status: string): vscode.ThemeIcon {
        switch (status) {
            case 'running':
                return new vscode.ThemeIcon('sync~spin');
            case 'completed':
                return new vscode.ThemeIcon('check');
            case 'failed':
                return new vscode.ThemeIcon('error');
            default:
                return new vscode.ThemeIcon('circle');
        }
    }

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }
}
