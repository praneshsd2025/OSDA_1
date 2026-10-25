#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>

void display_header(void);
void display_menu(void);
void display_process_information(pid_t pid, pid_t ppid, uid_t uid);
void display_system_call_details(void);
void display_process_relationship(pid_t pid, pid_t ppid);
void display_summary(pid_t pid, pid_t ppid, uid_t uid);
void display_all_information(pid_t pid, pid_t ppid, uid_t uid);
int get_menu_choice(void);

void display_header(void)
{
    printf("\n====================================================\n");
    printf("       OPERATING SYSTEM SYSTEM CALL ANALYZER\n");
    printf("====================================================\n");
    printf(" Demonstration of getpid(), getppid() and getuid()\n");
    printf("====================================================\n\n");
}

void display_menu(void)
{
    printf("\n-------------------- MAIN MENU ---------------------\n");
    printf("1. View Process Information\n2. View System Call Details\n");
    printf("3. Analyze Parent-Child Relationship\n4. Generate Process Summary\n");
    printf("5. Display Complete Report\n0. Exit Program\n");
    printf("----------------------------------------------------\n");
}

int get_menu_choice(void)
{
    int choice, result;
    printf("Enter your choice: ");
    result = scanf("%d", &choice);
    if (result != 1) {
        int character;
        while ((character = getchar()) != '\n' && character != EOF) { }
        printf("\nInvalid input. Please enter a number.\n");
        return -1;
    }
    if (choice < 0 || choice > 5) {
        printf("\nInvalid choice. Select an option from 0 to 5.\n");
        return -1;
    }
    return choice;
}

void display_process_information(pid_t pid, pid_t ppid, uid_t uid)
{
    printf("\n=============== PROCESS INFORMATION ================\n");
    printf("%-30s : %d\n", "Current Process ID (PID)", (int)pid);
    printf("%-30s : %d\n", "Parent Process ID (PPID)", (int)ppid);
    printf("%-30s : %d\n", "Real User ID (UID)", (int)uid);
    printf("====================================================\n");
    printf("\nExplanation:\n- PID identifies the currently running process.\n");
    printf("- PPID identifies the parent process.\n");
    printf("- UID identifies the real user associated with it.\n");
}

void display_system_call_details(void)
{
    printf("\n=============== SYSTEM CALL DETAILS ================\n");
    printf("\n1. getpid()  : Retrieves the current process ID.\n");
    printf("2. getppid() : Retrieves the parent process ID.\n");
    printf("3. getuid()  : Retrieves the real user ID.\n");
    printf("\nThese functions are provided by the POSIX/Unix API.\n");
    printf("====================================================\n");
}

void display_process_relationship(pid_t pid, pid_t ppid)
{
    printf("\n============= PROCESS RELATIONSHIP =================\n");
    printf("Current Process : PID %d\nParent Process  : PID %d\n", (int)pid, (int)ppid);
    if (pid == ppid)
        printf("Relationship    : PID and PPID are equal.\n");
    else if (ppid > 0)
        printf("Relationship    : The current process has a parent.\n");
    else
        printf("Relationship    : Parent PID is not positive.\n");
    printf("====================================================\n");
}

void display_summary(pid_t pid, pid_t ppid, uid_t uid)
{
    printf("\n================ PROCESS SUMMARY ===================\n");
    printf("Process ID        : %d\n", (int)pid);
    printf("Parent Process ID : %d\n", (int)ppid);
    printf("Real User ID      : %d\n", (int)uid);
    printf("Process ID Check  : %s\n", pid > 0 ? "Valid" : "Check required");
    printf("Parent ID Check   : %s\n", ppid > 0 ? "Available" : "Not positive");
    printf("User ID Status    : Retrieved\n");
    printf("====================================================\n");
}

void display_all_information(pid_t pid, pid_t ppid, uid_t uid)
{
    display_process_information(pid, ppid, uid);
    display_system_call_details();
    display_process_relationship(pid, ppid);
    display_summary(pid, ppid, uid);
}

int main(void)
{
    pid_t pid = getpid();
    pid_t ppid = getppid();
    uid_t uid = getuid();
    int choice;

    display_header();

    /* Machine-readable values used by the Streamlit dashboard. */
    printf("PID=%d\nPPID=%d\nUID=%d\n", (int)pid, (int)ppid, (int)uid);
    printf("\nProcess information retrieved successfully.\n");

    do {
        display_menu();
        choice = get_menu_choice();
        switch (choice) {
            case 1: display_process_information(pid, ppid, uid); break;
            case 2: display_system_call_details(); break;
            case 3: display_process_relationship(pid, ppid); break;
            case 4: display_summary(pid, ppid, uid); break;
            case 5: display_all_information(pid, ppid, uid); break;
            case 0:
                printf("\nProgram terminated successfully.\n");
                printf("Thank you for using the System Call Analyzer.\n");
                break;
            case -1: printf("Please try again.\n"); break;
        }
    } while (choice != 0);

    return EXIT_SUCCESS;
}
